"""04·10편: 주문 목록을 가져오는 네 가지 방법의 시간 비교(실행마다 값이 다르다).

사용: python tools/bench_relations.py [주문 수]
DB_PORT 환경 변수로 지연 프록시(tools/latency_proxy.py) 포트를 가리키면 네트워크 지연을 흉내 낸다.
데이터는 항상 5432 직접 연결(SEED_PORT)로 만든다.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django  # noqa: E402

django.setup()
import psycopg  # noqa: E402
from django.conf import settings  # noqa: E402

from core import orders  # noqa: E402
from core.querylog import capture  # noqa: E402


def seed(n_orders: int) -> None:
    d = settings.DB
    port = os.environ.get("SEED_PORT", "54329")
    with psycopg.connect(f"host={d['HOST']} port={port} dbname={d['NAME']} user={d['USER']} "
                         f"password={d['PASSWORD']}", autocommit=True) as conn:
        conn.execute(open("sql/001_schema.sql", encoding="utf-8").read())
        conn.execute("INSERT INTO product (sku, name, category, price, stock) "
                     "SELECT 'P-' || g, 'p', 'book', 100, 10 FROM generate_series(1, 100) g")
        conn.execute("INSERT INTO customer (email, name) "
                     "SELECT 'c' || g || '@example.com', 'c' FROM generate_series(1, 100) g")
        conn.execute("INSERT INTO orders (customer_id) SELECT 1 + g %% 100 FROM generate_series(1, %s) g",
                     [n_orders])
        conn.execute("INSERT INTO order_item (order_id, product_id, quantity, unit_price) "
                     "SELECT o.id, 1 + (o.id + i) % 100, 1, 100 FROM orders o, generate_series(1, 5) i")
        conn.execute("ANALYZE")


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    seed(n)
    settings.SHOP_DB_BACKEND = "a"
    orders.list_two_queries(n)  # 연결 맺기를 측정에서 뺀다
    for label, fn in (("N+1", orders.list_n_plus_1), ("JOIN 후 묶기", orders.list_flat_join),
                      ("2쿼리(IN)", orders.list_two_queries), ("json_agg 1쿼리", orders.list_json_agg)):
        limit = n * 5 if fn is orders.list_flat_join else n
        t = time.perf_counter()
        with capture() as q:
            fn(limit)
        print(f"{label:<14} 쿼리 {len(q):>4}번 {(time.perf_counter() - t) * 1000:8.1f}ms")


if __name__ == "__main__":
    main()
