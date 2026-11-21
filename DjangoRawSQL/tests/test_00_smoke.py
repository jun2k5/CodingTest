from core.db import get_db


def test_select_one(backend):
    db = get_db()
    assert db.fetch_one("SELECT 1 AS one") == {"one": 1}


def test_schema_tables(backend):
    rows = get_db().fetch_all(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY table_name"
    )
    assert [r["table_name"] for r in rows] == [
        "customer", "order_item", "orders", "product", "review"
    ]
