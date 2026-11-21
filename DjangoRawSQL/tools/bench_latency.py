"""10편: 왕복 지연을 넣고 04편(연관 조회)·02편(대량 입력) 방법을 다시 잰다(실행마다 값이 다르다).

지연 프록시를 한 방향 0ms(직접), 0.5ms, 5ms로 바꿔 가며 같은 작업을 방식 B 풀로 실행한다.
"""
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django  # noqa: E402

django.setup()
import psycopg  # noqa: E402
from django.conf import settings  # noqa: E402
from psycopg.rows import dict_row  # noqa: E402
from psycopg_pool import ConnectionPool  # noqa: E402

from core import orders, products  # noqa: E402
from shop_b import db as b_db  # noqa: E402
from tools.bench_relations import seed  # noqa: E402
from tools.latency_proxy import start_in_thread  # noqa: E402

DIRECT = "host=127.0.0.1 port=54329 dbname=shop user=shop password=shop"


def use_port(port: int) -> None:
    b_db.close_pool()
    b_db._pool = ConnectionPool(DIRECT.replace("54329", str(port)), min_size=1, max_size=2, open=True,
                                kwargs={"row_factory": dict_row, "autocommit": True})
    for _ in range(3):
        b_db.fetch_one("SELECT 1 AS x")   # 연결 맺기를 측정에서 뺀다


def timed(fn) -> float:
    runs = []
    for _ in range(3):
        t = time.perf_counter()
        fn()
        runs.append((time.perf_counter() - t) * 1000)
    return statistics.median(runs)


def rtt() -> float:
    return timed(lambda: b_db.fetch_one("SELECT 1 AS x"))


def main():
    settings.SHOP_DB_BACKEND = "b"
    seed(100)   # 주문 100개 × 항목 5개
    targets = [("직접", 54329)]
    for port, d in ((54340, 0.5), (54341, 5.0)):
        start_in_thread(port, 54329, d)
        targets.append((f"+{d}ms", port))
    jobs = [("N+1(201쿼리)", lambda: orders.list_n_plus_1(100)),
            ("2쿼리(IN)", lambda: orders.list_two_queries(100)),
            ("json_agg 1쿼리", lambda: orders.list_json_agg(100))]
    rows = [{"sku": f"L-{i}", "name": "p", "category": "book", "price": 1, "stock": 1} for i in range(500)]
    for label, port in targets:
        use_port(port)
        out = [f"왕복 {rtt():5.2f}ms"]
        for name, fn in jobs:
            out.append(f"{name} {timed(fn):8.1f}ms")
        with psycopg.connect(DIRECT, autocommit=True) as c:
            c.execute("DELETE FROM product WHERE sku LIKE 'L%%'", [])
        t = time.perf_counter()
        for r in rows[:100]:
            products.create(r)
        out.append(f"반복 INSERT 100행 {(time.perf_counter() - t) * 1000:8.1f}ms")
        t = time.perf_counter()
        products.bulk_create([{**r, "sku": "L2-" + r["sku"]} for r in rows[:100]])
        out.append(f"unnest 100행 {(time.perf_counter() - t) * 1000:6.1f}ms")
        print(f"[{label}] " + " | ".join(out))
    b_db.close_pool()


if __name__ == "__main__":
    main()
