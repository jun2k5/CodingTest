"""09편: 연결 수명, 풀, 기본 타임아웃, 트랜잭션 범위."""
import threading
import time

import pytest
from django.core.signals import request_finished, request_started
from django.db import InterfaceError, OperationalError, connection, connections, transaction
from psycopg_pool import PoolTimeout

from core import products, services
from tests.conftest import product_row, run_concurrently


def pid_of(conn) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT pg_backend_pid()")
        return cur.fetchone()[0]


def fake_request(conn) -> int:
    """Django가 요청 앞뒤로 보내는 신호를 그대로 보내 연결 수명 처리를 흉내 낸다."""
    request_started.send(sender=None)
    try:
        return pid_of(conn)
    finally:
        request_finished.send(sender=None)


@pytest.fixture
def conn_max_age():
    original = connection.settings_dict["CONN_MAX_AGE"]

    def set_age(age):
        connection.close()
        connection.settings_dict["CONN_MAX_AGE"] = age

    yield set_age
    set_age(original)


def test_conn_max_age_0_reconnects_every_request(conn_max_age):
    conn_max_age(0)
    assert fake_request(connection) != fake_request(connection)   # 요청마다 새 연결(접속 비용 매번)


def test_conn_max_age_keeps_connection_between_requests(conn_max_age):
    conn_max_age(60)
    assert fake_request(connection) == fake_request(connection)


def test_django_pool_reuses_connections(conn_max_age):
    conn_max_age(0)
    plain = {fake_request(connection) for _ in range(10)}
    pooled = {fake_request(connections["pooled"]) for _ in range(10)}
    assert len(plain) == 10          # 요청 10번 = 접속 10번
    assert len(pooled) <= 2          # 풀은 요청이 끝나도 연결을 닫지 않고 돌려받아 다시 준다


def test_b_pool_exhaustion_times_out(settings):
    from shop_b.db import get_pool

    settings.SHOP_DB_BACKEND = "b"
    pool = get_pool()
    hold, release = threading.Barrier(pool.max_size + 1, timeout=5), threading.Event()

    def borrow_and_hold():
        with pool.connection():
            hold.wait()
            release.wait(5)

    threads = [threading.Thread(target=borrow_and_hold) for _ in range(pool.max_size)]
    for t in threads:
        t.start()
    hold.wait()                                    # 풀의 연결을 모두 빌려 갔다
    t0 = time.perf_counter()
    with pytest.raises(PoolTimeout):
        with pool.connection(timeout=0.5):
            pass
    waited = time.perf_counter() - t0
    release.set()
    for t in threads:
        t.join()
    assert 0.4 < waited < 2.0                      # 무한정 기다리지 않고 정한 시간에 실패한다


def show(conn, name: str) -> str:
    with conn.cursor() as cur:
        cur.execute(f"SHOW {name}")
        return cur.fetchone()[0]


def test_connection_options_set_default_timeouts():
    tuned = connections["tuned"]
    assert (show(tuned, "lock_timeout"), show(tuned, "statement_timeout"),
            show(tuned, "idle_in_transaction_session_timeout")) == ("2s", "5s", "10s")
    assert show(connection, "statement_timeout") == "0"   # 기본 연결은 제한 없음


def test_idle_in_transaction_session_is_terminated():
    with connection.cursor() as cur:
        cur.execute("SET idle_in_transaction_session_timeout = '300ms'")
    with pytest.raises((OperationalError, InterfaceError)):   # 서버가 연결을 끊었다
        with transaction.atomic():
            products.create(product_row(1))
            time.sleep(0.8)                         # 트랜잭션을 연 채로 다른 일을 한다
            products.create(product_row(2))
    connection.close()


def slow_api():
    time.sleep(1.0)


def test_external_call_inside_transaction_blocks_others(backend):
    products.create(product_row(1))
    started = threading.Event()

    def other_request():
        started.wait(5)
        time.sleep(0.1)
        t = time.perf_counter()
        products.update(1, {"stock": 5})
        return time.perf_counter() - t

    results = run_concurrently(
        lambda: services.change_price_call_inside(1, 900, lambda: (started.set(), slow_api())),
        other_request,
    )
    assert results[1] > 0.7      # 관계없는 재고 수정이 외부 호출 시간만큼 기다렸다


def test_external_call_outside_transaction_does_not_block(backend):
    products.create(product_row(1))
    started = threading.Event()

    def other_request():
        started.wait(5)
        time.sleep(0.1)
        t = time.perf_counter()
        products.update(1, {"stock": 5})
        return time.perf_counter() - t

    results = run_concurrently(
        lambda: services.change_price_call_outside(1, 900, lambda: (started.set(), slow_api())),
        other_request,
    )
    assert results[1] < 0.3


def test_on_commit_runs_only_after_commit(settings):
    settings.SHOP_DB_BACKEND = "a"
    sent = []
    with transaction.atomic():
        products.create(product_row(1))
        transaction.on_commit(lambda: sent.append("메일"))
        assert sent == []
    assert sent == ["메일"]
    with pytest.raises(RuntimeError):
        with transaction.atomic():
            transaction.on_commit(lambda: sent.append("롤백된 메일"))
            raise RuntimeError
    assert sent == ["메일"]
