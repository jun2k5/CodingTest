"""06편: 인덱스를 직접 만들 수 없는 DB에서 근거를 모으고, 쿼리를 인덱스에 맞추기."""
import pytest
from django.db import connection

from core import dbstats
from core.db import get_db
from tests.conftest import OUTPUTS, explain
from tests.seed import run, seed_customers_orders, seed_products


@pytest.fixture
def shop():
    seed_products(1000)
    seed_customers_orders(customers=1000, orders_per_customer=20, items_per_order=3)


def workload():
    db = get_db()
    for i in range(1, 201):
        db.fetch_all("SELECT product_id, quantity FROM order_item WHERE order_id = %s", [i])
        db.fetch_one("SELECT id, name FROM customer WHERE id = %s", [i])


def flush_stats():
    with connection.cursor() as cur:
        cur.execute("SELECT pg_stat_force_next_flush()")
    with connection.cursor() as cur:
        cur.execute("SELECT 1")


def save(name: str, rows: list[dict]) -> None:
    lines = [" | ".join(str(v) for v in r.values()) for r in rows]
    (OUTPUTS / f"{name}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_pg_stat_statements_ranks_by_blocks(shop, settings):
    settings.SHOP_DB_BACKEND = "a"
    run("SELECT pg_stat_statements_reset()")
    workload()
    top = dbstats.top_statements(limit=2)
    save("06_top_statements", top)
    assert "order_item" in top[0]["query"] and top[0]["calls"] == 200
    assert top[0]["blocks_per_call"] > 100 * top[1]["blocks_per_call"]


def test_table_stats_show_seq_scans(shop, settings):
    settings.SHOP_DB_BACKEND = "a"
    flush_stats()   # 시드 단계에서 쌓인 통계를 먼저 반영한 뒤 지운다
    run("SELECT pg_stat_reset()")
    workload()
    flush_stats()
    rows = dbstats.table_scans(["customer", "order_item"])
    save("06_table_scans", rows)
    item = next(r for r in rows if r["relname"] == "order_item")
    assert item["seq_scan"] == 200 and item["seq_tup_read"] == 200 * 60000


def test_unused_index_has_zero_scans(shop, settings):
    settings.SHOP_DB_BACKEND = "a"
    run("CREATE INDEX orders_total_idx ON orders (total)")
    run("CREATE INDEX orders_customer_idx ON orders (customer_id)")
    flush_stats()
    run("SELECT pg_stat_reset()")
    for i in range(1, 51):
        get_db().fetch_all("SELECT id FROM orders WHERE customer_id = %s", [i])
    flush_stats()
    usage = {r["indexrelname"]: r["idx_scan"] for r in dbstats.index_usage("orders")}
    assert usage["orders_total_idx"] == 0 and usage["orders_customer_idx"] == 50


def test_function_on_column_skips_index(shop):
    run("CREATE INDEX customer_email_idx ON customer (email)")
    run("ANALYZE customer")
    assert "Seq Scan" in explain("SELECT id FROM customer WHERE lower(email) = 'c77@example.com'",
                                 save_as="06_lower_email")
    assert "Index Scan" in explain("SELECT id FROM customer WHERE email = 'c77@example.com'")


def test_cast_on_column_skips_index(shop):
    run("CREATE INDEX orders_created_idx ON orders (created_at)")
    run("ANALYZE orders")
    bad = explain("SELECT count(*) FROM orders WHERE created_at::date = '2026-01-02'",
                  save_as="06_date_cast")
    good = explain(
        "SELECT count(*) FROM orders WHERE created_at >= '2026-01-02' AND created_at < '2026-01-03'",
        save_as="06_date_range",
    )
    assert "Seq Scan" in bad and "Index" in good


def test_float_parameter_casts_bigint_column(shop):
    run("CREATE INDEX orders_customer_idx ON orders (customer_id)")
    run("ANALYZE orders")
    bad = explain("SELECT id FROM orders WHERE customer_id = %s", [77.0], save_as="06_float_param")
    good = explain("SELECT id FROM orders WHERE customer_id = %s", [77])
    assert "Seq Scan" in bad and "Index" in good


def test_prefix_like_needs_pattern_ops(shop):
    run("CREATE INDEX customer_email_idx ON customer (email)")
    run("ANALYZE customer")
    sql = "SELECT id FROM customer WHERE email LIKE 'c77%%'"
    assert "Seq Scan" in explain(sql, [], save_as="06_like_default")
    run("CREATE INDEX customer_email_pattern_idx ON customer (email text_pattern_ops)")
    run("ANALYZE customer")
    assert "customer_email_pattern_idx" in explain(sql, [], save_as="06_like_pattern_ops")


def test_create_index_concurrently_outside_transaction(shop, backend):
    db = get_db()
    with pytest.raises(Exception, match="cannot run inside a transaction block"):
        with db.transaction():
            db.execute("CREATE INDEX CONCURRENTLY orders_status_idx ON orders (status)")
    db.execute("CREATE INDEX CONCURRENTLY orders_status_idx ON orders (status)")
    names = [r["indexname"] for r in dbstats.existing_indexes("orders")]
    assert "orders_status_idx" in names
