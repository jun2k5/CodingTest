"""05편: 인덱스 수에 따른 INSERT 시간(실행마다 값이 다르다). 주문 20만 행을 한 문장으로 넣는다."""
import time

import psycopg

DSN = "host=localhost port=54329 dbname=shop user=shop password=shop"
EXTRA = [
    "CREATE INDEX b1_idx ON orders (customer_id)",
    "CREATE INDEX b2_idx ON orders (customer_id, created_at DESC)",
    "CREATE INDEX b3_idx ON orders (status)",
    "CREATE INDEX b4_idx ON orders (created_at)",
    "CREATE INDEX b5_idx ON orders (total)",
]

with psycopg.connect(DSN, autocommit=True) as conn:
    for n in (0, 1, 3, 5):
        conn.execute(open("sql/001_schema.sql", encoding="utf-8").read())
        conn.execute("INSERT INTO customer (email, name) "
                     "SELECT 'c' || g || '@example.com', 'c' FROM generate_series(1, 1000) g")
        for ddl in EXTRA[:n]:
            conn.execute(ddl)
        t = time.perf_counter()
        conn.execute("INSERT INTO orders (customer_id, total, created_at) "
                     "SELECT 1 + g % 1000, g % 50000, now() - g * interval '1 second' "
                     "FROM generate_series(1, 200000) g")
        print(f"PK + 추가 인덱스 {n}개: {time.perf_counter() - t:6.2f}s")
    conn.execute(open("sql/001_schema.sql", encoding="utf-8").read())
