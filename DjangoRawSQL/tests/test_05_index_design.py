"""05편: 인덱스를 직접 설계할 수 있을 때."""
import pytest

from tests.conftest import apply_sql, explain
from tests.seed import run, seed_customers_orders, seed_products


@pytest.fixture
def shop():
    seed_products(1000)
    seed_customers_orders(customers=1000, orders_per_customer=20, items_per_order=3)  # 주문 2만, 항목 6만


def relsize(name: str) -> int:
    from django.db import connection
    with connection.cursor() as cur:
        cur.execute("SELECT pg_relation_size(%s)", [name])
        return cur.fetchone()[0]


def test_fk_column_has_no_index_by_default(shop):
    from django.db import connection
    with connection.cursor() as cur:
        cur.execute("SELECT indexname FROM pg_indexes WHERE tablename = 'order_item' ORDER BY 1")
        assert [r[0] for r in cur.fetchall()] == ["order_item_pkey"]   # PK만 있다


def test_fk_index_changes_seq_scan_to_index_scan(shop):
    sql = "SELECT product_id, quantity FROM order_item WHERE order_id = 12345"
    assert "Seq Scan" in explain(sql, save_as="05_fk_before")
    run("CREATE INDEX order_item_order_id_idx ON order_item (order_id)")
    run("ANALYZE order_item")
    assert "Index Scan using order_item_order_id_idx" in explain(sql, save_as="05_fk_after")


RECENT = ("SELECT id, created_at FROM orders WHERE customer_id = 77 "
          "ORDER BY created_at DESC LIMIT 5")


def test_equality_column_first_avoids_sort(shop):
    run("CREATE INDEX orders_customer_created_idx ON orders (customer_id, created_at DESC)")
    run("ANALYZE orders")
    plan = explain(RECENT, save_as="05_order_good")
    assert "Index Scan using orders_customer_created_idx" in plan and "Sort" not in plan


def test_range_column_first_cannot_seek_by_customer(shop):
    run("CREATE INDEX orders_created_customer_idx ON orders (created_at, customer_id)")
    run("ANALYZE orders")
    plan = explain(RECENT, save_as="05_order_bad")
    assert "orders_customer_created_idx" not in plan
    assert "Sort" in plan or "Seq Scan" in plan or "Index Scan Backward" in plan


def test_leading_column_missing_from_where(shop):
    run("CREATE INDEX orders_customer_status_idx ON orders (customer_id, status)")
    run("ANALYZE orders")
    plan = explain("SELECT count(*) FROM orders WHERE status = 'paid'", save_as="05_leading_missing")
    assert "Seq Scan on orders" in plan


def test_partial_index_is_small_and_used(shop):
    run("CREATE INDEX orders_created_full_idx ON orders (created_at)")
    run("CREATE INDEX orders_pending_created_idx ON orders (created_at) WHERE status = 'pending'")
    run("ANALYZE orders")
    plan = explain(
        "SELECT id FROM orders WHERE status = 'pending' ORDER BY created_at LIMIT 10",
        save_as="05_partial",
    )
    assert "orders_pending_created_idx" in plan
    assert relsize("orders_pending_created_idx") * 3 < relsize("orders_created_full_idx")


def test_covering_index_allows_index_only_scan(shop):
    run("CREATE INDEX orders_customer_cover_idx ON orders (customer_id) INCLUDE (status, total)")
    run("VACUUM ANALYZE orders")   # visibility map을 채워야 테이블을 다시 읽지 않는다
    plan = explain("SELECT status, total FROM orders WHERE customer_id = 77", save_as="05_covering")
    assert "Index Only Scan using orders_customer_cover_idx" in plan and "Heap Fetches: 0" in plan


def test_project_index_file_applies(shop):
    apply_sql("002_indexes.sql")
    from django.db import connection
    with connection.cursor() as cur:
        cur.execute("SELECT count(*) FROM pg_indexes WHERE indexname LIKE '%%_idx'")
        assert cur.fetchone()[0] == 7


def test_column_order_changes_blocks_read(shop):
    from tests.conftest import buffers

    run("CREATE INDEX orders_created_customer_idx ON orders (created_at, customer_id)")
    run("ANALYZE orders")
    bad = buffers(RECENT)
    run("DROP INDEX orders_created_customer_idx")
    run("CREATE INDEX orders_customer_created_idx ON orders (customer_id, created_at DESC)")
    run("ANALYZE orders")
    good = buffers(RECENT)
    print(f"\n(created_at, customer_id) {bad} blocks / (customer_id, created_at) {good} blocks")
    assert good * 5 < bad
