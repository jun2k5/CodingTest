# DjangoRawSQL

velog 시리즈 [Django Raw SQL CRUD 고찰](https://velog.io/@jun2k5/djsql-00-series-intro)의 예제 코드다. ORM(모델·QuerySet·마이그레이션) 없이 Django와 PostgreSQL로 CRUD API를 만들고, 모든 주장을 실제 PostgreSQL 17에 대고 pytest로 확인한다.

- **두 가지 DB 접근 방식:** `shop_a/db.py`(Django `connection.cursor()` + `atomic`)와 `shop_b/db.py`(`psycopg_pool`, `autocommit=True`)가 같은 함수(`fetch_all`, `fetch_one`, `execute`, `executemany`, `transaction`)를 제공한다. `core/`의 SQL·리포지토리는 `core.db.get_db()`로 둘 중 하나를 고르고, 테스트는 `backend` fixture로 두 방식을 한 번씩 돈다.
- **스키마:** `sql/001_schema.sql`(FK 인덱스 없이 시작), `sql/002_indexes.sql`(05편에서 근거를 확인한 인덱스).
- **RDS:** 실제 RDS에서는 측정하지 않았다. 왕복 지연은 `tools/latency_proxy.py`로 흉내 냈다.

## 실행

```bash
docker compose up -d                      # postgres:17, localhost:54329 (로컬 전용 테스트 계정)
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # Windows. macOS/Linux는 .venv/bin/python
.venv/Scripts/python -m pytest -v
```

`outputs/`의 EXPLAIN 결과는 테스트가 실행될 때 다시 만들어진다. `tools/bench_*.py`는 시간 측정 스크립트라 실행마다 값이 다르다.

| # | 주제 | 코드 | 테스트 | 글 |
|---|---|---|---|---|
| 01 | ORM 없이 DB 쓰기: connection.cursor()와 psycopg_pool | [shop_a/db.py](shop_a/db.py), [shop_b/db.py](shop_b/db.py) | [test_01](tests/test_01_backends.py) | [글](https://velog.io/@jun2k5/djsql-01-access-layer) |
| 02 | SQL로 짜는 CRUD | [core/products.py](core/products.py), [api/views.py](api/views.py), [bench_bulk](tools/bench_bulk.py) | [test_02](tests/test_02_crud.py) | [글](https://velog.io/@jun2k5/djsql-02-crud) |
| 03 | 목록 조회: 화이트리스트, keyset | [core/listing.py](core/listing.py) | [test_03](tests/test_03_listing.py) | [글](https://velog.io/@jun2k5/djsql-03-listing) |
| 04 | 참조와 역참조 | [core/orders.py](core/orders.py), [core/product_stats.py](core/product_stats.py), [bench_relations](tools/bench_relations.py) | [test_04](tests/test_04_relations.py) | [글](https://velog.io/@jun2k5/djsql-04-relations) |
| 05 | 인덱스 ①: 직접 설계 | [sql/002_indexes.sql](sql/002_indexes.sql), [bench_index_write](tools/bench_index_write.py) | [test_05](tests/test_05_index_design.py) | [글](https://velog.io/@jun2k5/djsql-05-index-design) |
| 06 | 인덱스 ②: 남의 DB | [core/dbstats.py](core/dbstats.py) | [test_06](tests/test_06_index_evidence.py) | [글](https://velog.io/@jun2k5/djsql-06-index-evidence) |
| 07 | 동시성 ①: API 안에서 | [core/inventory.py](core/inventory.py), [core/retry.py](core/retry.py) | [test_07](tests/test_07_concurrency_api.py) | [글](https://velog.io/@jun2k5/djsql-07-concurrency-api) |
| 08 | 동시성 ②: 외부 쓰기와 함께 | [core/external.py](core/external.py) | [test_08](tests/test_08_concurrency_external.py) | [글](https://velog.io/@jun2k5/djsql-08-concurrency-external) |
| 09 | 커넥션과 트랜잭션 | [config/settings.py](config/settings.py), [core/services.py](core/services.py) | [test_09](tests/test_09_connections.py) | [글](https://velog.io/@jun2k5/djsql-09-connections) |
| 10 | RDS에서 달라지는 것 | [latency_proxy](tools/latency_proxy.py), [bench_latency](tools/bench_latency.py) | [test_10](tests/test_10_rds.py) | [글](https://velog.io/@jun2k5/djsql-10-rds) |
| 11 | 체크리스트와 선택표 | - | - | [글](https://velog.io/@jun2k5/djsql-11-checklist) |
