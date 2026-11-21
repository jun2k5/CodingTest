"""01편: connection.cursor()(A)와 psycopg_pool(B)의 차이."""
import pytest

from core import products
from core.db import get_db
from tests.conftest import product_row


def count_products() -> int:
    return get_db().fetch_one("SELECT count(*) AS n FROM product")["n"]


def test_same_repository_code_on_both_backends(backend):
    created = products.create(product_row(1))
    assert products.get(created["id"]) == created


def test_error_in_transaction_rolls_back_whole_block(backend):
    db = get_db()
    with pytest.raises(RuntimeError):
        with db.transaction():
            products.create(product_row(1))
            raise RuntimeError("중간에 실패")
    assert count_products() == 0


def test_nested_transaction_becomes_savepoint(backend):
    db = get_db()
    with db.transaction():
        products.create(product_row(1))
        try:
            with db.transaction():
                products.create(product_row(2))
                raise RuntimeError("안쪽만 실패")
        except RuntimeError:
            pass
    skus = [r["sku"] for r in db.fetch_all("SELECT sku FROM product ORDER BY id")]
    assert skus == ["SKU-00001"]


def test_without_transaction_each_statement_commits(backend):
    products.create(product_row(1))
    with pytest.raises(Exception):
        products.create(product_row(1))  # sku 중복
    assert count_products() == 1  # 첫 INSERT는 이미 커밋됐다


def backend_pid() -> int:
    return get_db().fetch_one("SELECT pg_backend_pid() AS pid")["pid"]


def test_a_reuses_one_django_connection_per_thread(settings):
    settings.SHOP_DB_BACKEND = "a"
    assert backend_pid() == backend_pid()


def test_b_borrows_connection_from_pool_per_call(settings):
    settings.SHOP_DB_BACKEND = "b"
    from shop_b.db import get_pool

    pids = {backend_pid() for _ in range(10)}
    stats = get_pool().get_stats()
    assert len(pids) <= settings.SHOP_B_POOL["max_size"]
    assert stats["pool_size"] <= settings.SHOP_B_POOL["max_size"]


def test_b_transaction_keeps_one_connection(settings):
    settings.SHOP_DB_BACKEND = "b"
    with get_db().transaction():
        first, second = backend_pid(), backend_pid()
    assert first == second
