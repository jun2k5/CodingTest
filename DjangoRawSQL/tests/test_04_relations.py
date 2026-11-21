"""04편: 정참조·역참조를 SQL로 가져오는 방법과 함정."""
from core import orders, product_stats
from core.querylog import capture
from tests.conftest import explain
from tests.seed import run, seed_customers_orders, seed_products, seed_reviews


def seed_small():
    seed_products(50)
    seed_customers_orders(customers=5, orders_per_customer=4, items_per_order=3)  # 주문 20개, 항목 60개


def test_n_plus_1_sends_1_plus_2n_queries(backend):
    seed_small()
    with capture() as q:
        result = orders.list_n_plus_1(limit=20)
    assert len(result) == 20 and len(q) == 1 + 2 * 20


def test_two_queries_same_result(backend):
    seed_small()
    expected = orders.list_n_plus_1(limit=20)
    with capture() as q:
        result = orders.list_two_queries(limit=20)
    assert result == expected and len(q) == 2


def test_json_agg_one_query_same_result(backend):
    seed_small()
    expected = orders.list_n_plus_1(limit=20)
    with capture() as q:
        result = orders.list_json_agg(limit=20)
    assert result == expected and len(q) == 1


def test_flat_join_returns_order_times_item_rows(backend):
    seed_small()
    with capture() as q:
        result = orders.list_flat_join(limit=1000)
    assert len(result) == 20 and len(q) == 1
    from core.db import get_db
    joined = get_db().fetch_one(
        "SELECT count(*) AS n FROM orders o LEFT JOIN order_item i ON i.order_id = o.id")
    assert joined["n"] == 60  # 주문 20개가 60행이 되어 전송된다


def test_flat_join_limit_cuts_items_of_last_order(backend):
    seed_small()
    result = orders.list_flat_join(limit=10)   # "주문 10개"를 원했지만 LIMIT은 행에 걸린다
    assert len(result) == 4
    assert len(result[-1]["items"]) == 1       # 마지막 주문은 항목 3개 중 1개만 왔다


def test_two_reverse_joins_inflate_counts(backend):
    seed_products(1)
    seed_customers_orders(customers=1, orders_per_customer=2, items_per_order=1)  # 판매 행 2개, 수량 2씩
    seed_reviews(per_product=3)
    assert product_stats.stats_naive_join(1) == {"reviews": 6, "sold": 12}   # 리뷰 3 × 판매 행 2로 곱해졌다
    assert product_stats.stats(1) == {"reviews": 3, "sold": 4}


def test_latest_reviews_per_product_with_lateral(backend):
    seed_products(3)
    run("INSERT INTO customer (email, name) VALUES ('a@example.com', 'a')")
    seed_reviews(per_product=5)
    rows = product_stats.latest_reviews([1, 2, 3], per_product=2)
    per = {}
    for r in rows:
        per.setdefault(r["product_id"], []).append(r["review_id"])
    assert {k: len(v) for k, v in per.items()} == {1: 2, 2: 2, 3: 2}


def test_explain_reverse_lookup_without_fk_index():
    seed_products(1000)
    seed_customers_orders(customers=1000, orders_per_customer=10, items_per_order=3)  # 항목 3만 행
    plan = explain(
        "SELECT order_id, product_id FROM order_item WHERE order_id = ANY(ARRAY[1,2,3,4,5,6,7,8,9,10]::bigint[])",
        save_as="04_items_no_fk_index",
    )
    assert "Seq Scan on order_item" in plan   # FK 컬럼에 인덱스가 없어 전체를 읽는다
