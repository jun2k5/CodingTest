"""실험용 대량 데이터. generate_series로 DB 안에서 만들어 빠르고, 값이 항상 같다."""
from django.db import connection

CATEGORIES = "ARRAY['book','toy','food','tool','game']"


def run(sql: str, params=None) -> None:
    with connection.cursor() as cur:
        cur.execute(sql, params)


def seed_products(n: int) -> None:
    # price는 0~49,999 사이에서 겹치는 값이 많도록 만든다.
    run(
        "INSERT INTO product (sku, name, category, price, stock, created_at) "
        "SELECT 'P-' || g, '상품 ' || g, "
        f"({CATEGORIES})[1 + g %% 5], (g * 7919) %% 50000, 100, "
        "timestamptz '2026-01-01' + g * interval '1 minute' "
        "FROM generate_series(1, %s) AS g",
        [n],
    )
    run("ANALYZE product")


def seed_customers_orders(customers: int, orders_per_customer: int, items_per_order: int) -> None:
    run(
        "INSERT INTO customer (email, name) "
        "SELECT 'c' || g || '@example.com', '고객 ' || g FROM generate_series(1, %s) AS g",
        [customers],
    )
    run(
        "INSERT INTO orders (customer_id, status, total, created_at) "
        "SELECT c, (ARRAY['pending','paid','shipped','cancelled'])[1 + (c + o) %% 4], 0, "
        "timestamptz '2026-01-01' + (c * 100 + o) * interval '1 minute' "
        "FROM generate_series(1, %s) AS c, generate_series(1, %s) AS o",
        [customers, orders_per_customer],
    )
    run(
        "INSERT INTO order_item (order_id, product_id, quantity, unit_price) "
        "SELECT o.id, 1 + (o.id * 31 + i) %% (SELECT count(*) FROM product), 1 + i %% 3, 1000 "
        "FROM orders o, generate_series(1, %s) AS i",
        [items_per_order],
    )
    run("ANALYZE customer; ANALYZE orders; ANALYZE order_item")


def seed_reviews(per_product: int) -> None:
    run(
        "INSERT INTO review (product_id, customer_id, rating, body) "
        "SELECT p.id, 1 + (p.id + r) %% (SELECT count(*) FROM customer), 1 + (p.id + r) %% 5, '리뷰' "
        "FROM product p, generate_series(1, %s) AS r",
        [per_product],
    )
    run("ANALYZE review")
