"""02편: 대량 입력 세 가지 방법의 시간 비교(실행마다 값이 다르다).

사용: python tools/bench_bulk.py [행 수]
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django  # noqa: E402

django.setup()
from django.db import connection  # noqa: E402

from core import products  # noqa: E402


def reset():
    with connection.cursor() as cur:
        cur.execute((open("sql/001_schema.sql", encoding="utf-8")).read())


def rows(n, prefix):
    return [{"sku": f"{prefix}-{i}", "name": f"상품 {i}", "category": "book", "price": i, "stock": 1}
            for i in range(n)]


def loop_insert(rs):
    for r in rs:
        products.create(r)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    for backend in ("a", "b"):
        from django.conf import settings
        settings.SHOP_DB_BACKEND = backend
        for label, fn in (("반복문 INSERT", loop_insert),
                          ("executemany", products.bulk_create_executemany),
                          ("unnest 한 번", products.bulk_create)):
            reset()
            data = rows(n, label[:2])
            t = time.perf_counter()
            fn(data)
            print(f"{backend} {label:<14} {n}행 {time.perf_counter() - t:7.3f}s")
    from shop_b.db import close_pool
    close_pool()


if __name__ == "__main__":
    main()
