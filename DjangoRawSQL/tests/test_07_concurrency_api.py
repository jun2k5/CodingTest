"""07편: API 안에서의 동시성 - 갱신 손실, 원자적 UPDATE, FOR UPDATE, 낙관적 잠금, 교착 상태."""
import threading

import pytest

from core import inventory, products
from core.db import get_db
from core.retry import run_with_retry, sqlstate
from tests.conftest import product_row, run_concurrently
from tests.seed import run

URL = "/api/products/"


def stock(pid=1) -> int:
    return products.get(pid)["stock"]


def test_read_then_write_loses_update(backend):
    products.create(product_row(1, stock=10))
    barrier = threading.Barrier(2, timeout=5)
    run_concurrently(lambda: inventory.reserve_read_then_write(1, 1, barrier.wait),
                     lambda: inventory.reserve_read_then_write(1, 1, barrier.wait))
    assert stock() == 9   # 두 번 팔았는데 한 번만 빠졌다


def test_atomic_update_never_goes_negative(backend):
    products.create(product_row(1, stock=10))
    results = run_concurrently(*[lambda: inventory.reserve_atomic(1, 1) for _ in range(20)])
    ok = [r for r in results if isinstance(r, int)]
    sold_out = [r for r in results if isinstance(r, inventory.OutOfStock)]
    assert (len(ok), len(sold_out), stock()) == (10, 10, 0)


def test_select_for_update_serializes_read_and_write(backend):
    products.create(product_row(1, stock=10))
    results = run_concurrently(*[lambda: inventory.reserve_for_update(1, 1) for _ in range(12)])
    assert sum(isinstance(r, int) for r in results) == 10 and stock() == 0


def test_reserve_api_returns_409_when_sold_out(backend, client):
    products.create(product_row(1, stock=1))
    assert client.post(f"{URL}1/reserve/", {"qty": 1}, format="json").status_code == 200
    assert client.post(f"{URL}1/reserve/", {"qty": 1}, format="json").status_code == 409


def test_if_match_rejects_stale_version_with_412(backend, client):
    products.create(product_row(1))
    etag = client.get(f"{URL}1/").headers["ETag"]                         # 두 사용자가 같은 버전을 읽었다
    first = client.patch(f"{URL}1/", {"price": 5000}, format="json", HTTP_IF_MATCH=etag)
    second = client.patch(f"{URL}1/", {"price": 7000}, format="json", HTTP_IF_MATCH=etag)
    assert (first.status_code, second.status_code) == (200, 412)
    assert products.get(1)["price"] == 5000                                # 늦은 쪽이 덮어쓰지 못했다


def test_lock_order_mismatch_causes_deadlock(backend):
    products.create(product_row(1, stock=10))
    products.create(product_row(2, stock=10))
    run("INSERT INTO customer (email, name) VALUES ('a@example.com', 'a')")
    barrier = threading.Barrier(2, timeout=5)
    results = run_concurrently(
        lambda: inventory.place_order(1, [(1, 1), (2, 1)], lock_sorted=False, between=barrier.wait),
        lambda: inventory.place_order(1, [(2, 1), (1, 1)], lock_sorted=False, between=barrier.wait),
    )
    states = sorted(sqlstate(r) if isinstance(r, Exception) else "ok" for r in results)
    assert states == ["40P01", "ok"]   # PostgreSQL이 한쪽을 교착 상태로 끊는다


def test_sorted_lock_order_avoids_deadlock(backend):
    products.create(product_row(1, stock=100))
    products.create(product_row(2, stock=100))
    run("INSERT INTO customer (email, name) VALUES ('a@example.com', 'a')")
    jobs = [lambda: inventory.place_order(1, [(1, 1), (2, 1)]),
            lambda: inventory.place_order(1, [(2, 1), (1, 1)])] * 10
    results = run_concurrently(*jobs)
    assert all(isinstance(r, int) for r in results)
    assert (stock(1), stock(2)) == (80, 80)


def rr_decrement(barrier=None):
    db = get_db()
    with db.transaction():
        db.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
        db.fetch_one("SELECT stock FROM product WHERE id = 1")   # 스냅샷이 여기서 정해진다
        if barrier:
            barrier.wait()
        db.execute("UPDATE product SET stock = stock - 1 WHERE id = 1")


def test_repeatable_read_raises_serialization_failure(backend):
    products.create(product_row(1, stock=10))
    barrier = threading.Barrier(2, timeout=5)
    results = run_concurrently(lambda: rr_decrement(barrier), lambda: rr_decrement(barrier))
    assert sorted(str(sqlstate(r)) for r in results) == ["40001", "None"]
    assert stock() == 9


def test_retry_reruns_whole_transaction(backend):
    products.create(product_row(1, stock=10))
    barrier = threading.Barrier(2, timeout=5)
    calls = {"n": 0}

    def once_with_barrier():
        calls["n"] += 1
        rr_decrement(barrier if calls["n"] <= 2 else None)

    results = run_concurrently(lambda: run_with_retry(once_with_barrier),
                               lambda: run_with_retry(once_with_barrier))
    assert results == [None, None] and stock() == 8


def test_bad_input_returns_400_not_500(backend, client):
    products.create(product_row(1))
    assert client.patch(f"{URL}1/", {"price": 1}, format="json", HTTP_IF_MATCH='"abc"').status_code == 400
    assert client.post(f"{URL}1/reserve/", {"qty": "many"}, format="json").status_code == 400
