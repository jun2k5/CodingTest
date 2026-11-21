"""08편: 외부 쓰기(ETL 배치 등)와 함께 쓰는 DB - lock_timeout, NOWAIT, SKIP LOCKED, upsert, 멱등 키, xmin."""
import threading
import time
from datetime import datetime, timedelta, timezone

import psycopg
import pytest

from core import external, inventory, products
from core.errors import VersionConflict
from core.retry import sqlstate
from shop_b.db import conninfo
from tests.conftest import product_row, run_concurrently
from tests.seed import run


class ExternalWriter:
    """API와 상관없는 다른 시스템. 자기 연결로 행을 잠그고 한동안 놓지 않는다(긴 배치)."""

    def __init__(self, sql: str, hold: float):
        self.sql, self.hold = sql, hold
        self.locked = threading.Event()
        self.thread = threading.Thread(target=self._run)

    def _run(self):
        with psycopg.connect(conninfo()) as conn:   # autocommit=False: 트랜잭션이 열린 채로 있다
            conn.execute(self.sql)
            self.locked.set()
            time.sleep(self.hold)
            conn.commit()

    def __enter__(self):
        self.thread.start()
        assert self.locked.wait(5)
        return self

    def __exit__(self, *exc):
        self.thread.join(10)


def test_lock_timeout_fails_fast_instead_of_waiting(backend):
    products.create(product_row(1))
    with ExternalWriter("UPDATE product SET name = 'ETL' WHERE id = 1", hold=2.0):
        t = time.perf_counter()
        with pytest.raises(Exception) as e:
            external.update_price_with_lock_timeout(1, 5000, timeout_ms=200)
        elapsed = time.perf_counter() - t
    assert sqlstate(e.value) == "55P03" and elapsed < 1.0


def test_without_lock_timeout_api_waits_for_batch(backend):
    products.create(product_row(1))
    with ExternalWriter("UPDATE product SET name = 'ETL' WHERE id = 1", hold=1.0):
        t = time.perf_counter()
        external.update_price_with_lock_timeout(1, 5000, timeout_ms=0)   # 0 = 무한 대기(기본값)
        elapsed = time.perf_counter() - t
    assert elapsed > 0.8


def test_nowait_fails_immediately(backend):
    products.create(product_row(1))
    with ExternalWriter("SELECT 1 FROM product WHERE id = 1 FOR UPDATE", hold=1.0):
        with pytest.raises(Exception) as e:
            external.reserve_nowait(1, 1)
    assert sqlstate(e.value) == "55P03"


def test_set_local_cannot_take_parameter(settings):
    settings.SHOP_DB_BACKEND = "b"
    from core.db import get_db
    db = get_db()
    with pytest.raises(psycopg.errors.SyntaxError):
        with db.transaction():
            db.execute("SET LOCAL lock_timeout = %s", ["200ms"])


def test_set_local_timeout_rejects_unknown_name(backend):
    from core.db import get_db
    with pytest.raises(ValueError):
        with get_db().transaction():
            external.set_local_timeout("work_mem; DROP TABLE product", 1)


def test_set_local_resets_after_transaction(backend):
    from core.db import get_db
    db = get_db()
    with db.transaction():
        external.set_local_timeout("lock_timeout", 300)
        inside = db.fetch_one("SHOW lock_timeout")["lock_timeout"]
    outside = db.fetch_one("SHOW lock_timeout")["lock_timeout"]
    assert (inside, outside) == ("300ms", "0")


def test_statement_timeout_cancels_long_query(backend):
    with pytest.raises(Exception) as e:
        external.run_with_statement_timeout("SELECT pg_sleep(2)", timeout_ms=100)
    assert sqlstate(e.value) == "57014"


def test_skip_locked_workers_never_take_same_order(backend):
    run("INSERT INTO customer (email, name) VALUES ('a@example.com', 'a')")
    run("INSERT INTO orders (customer_id) SELECT 1 FROM generate_series(1, 100)")
    results = run_concurrently(*[lambda: external.claim_pending_orders(10) for _ in range(10)])
    claimed = [i for r in results for i in r]
    assert len(claimed) == 100 and len(set(claimed)) == 100


def test_upsert_does_not_overwrite_newer_row(backend):
    products.create(product_row(1, price=1000))
    newer = products.update(1, {"price": 2000})["updated_at"]          # API가 방금 고쳤다
    stale = {**product_row(1, price=500), "updated_at": newer - timedelta(hours=1)}
    fresh = {**product_row(2, price=700), "updated_at": datetime.now(timezone.utc)}
    assert external.etl_upsert([stale, fresh]) == 1                   # 새 행 1개만 반영
    assert products.get(1)["price"] == 2000


def test_upsert_conflict_still_consumes_identity(backend):
    products.create(product_row(1))
    now = datetime.now(timezone.utc)
    external.etl_upsert([{**product_row(1), "updated_at": now - timedelta(days=1)},
                         {**product_row(2, price=700), "updated_at": now}])
    from core.db import get_db
    row = get_db().fetch_one("SELECT id, price FROM product WHERE sku = 'SKU-00002'")
    assert row == {"id": 3, "price": 700}   # 충돌한 행도 id 2를 써 버렸다(빈 번호)


def test_version_column_misses_external_update(backend):
    products.create(product_row(1, price=1000))
    seen = products.get(1)
    run("UPDATE product SET price = 1500 WHERE id = 1")                # ETL은 version을 모른다
    inventory.update_if_version(1, {"price": 3000}, seen["version"])   # 충돌을 못 잡고 덮어쓴다
    assert products.get(1)["price"] == 3000


def test_xmin_detects_any_writer(backend):
    products.create(product_row(1, price=1000))
    seen = external.get_with_xmin(1)
    run("UPDATE product SET price = 1500 WHERE id = 1")
    with pytest.raises(VersionConflict):
        external.update_price_if_xmin(1, 3000, seen["row_version"])
    fresh = external.get_with_xmin(1)
    assert external.update_price_if_xmin(1, 3000, fresh["row_version"])["price"] == 3000


def test_idempotency_key_creates_one_order(backend, client):
    products.create(product_row(1, stock=10))
    run("INSERT INTO customer (email, name) VALUES ('a@example.com', 'a')")
    body = {"customer_id": 1, "product_id": 1, "qty": 2}
    first = client.post("/api/orders/", body, format="json", HTTP_IDEMPOTENCY_KEY="k-1")
    again = client.post("/api/orders/", body, format="json", HTTP_IDEMPOTENCY_KEY="k-1")
    assert (first.status_code, again.status_code) == (201, 200)
    assert first.json() == again.json() and products.get(1)["stock"] == 8


def test_idempotency_key_under_concurrent_retries(backend):
    products.create(product_row(1, stock=10))
    run("INSERT INTO customer (email, name) VALUES ('a@example.com', 'a')")
    results = run_concurrently(*[lambda: external.create_order_idempotent("k-2", 1, 1, 1) for _ in range(8)])
    assert len({r[0] for r in results}) == 1 and sum(r[1] for r in results) == 1
    assert products.get(1)["stock"] == 9


def test_order_with_missing_field_returns_400(backend, client):
    res = client.post("/api/orders/", {"customer_id": 1}, format="json", HTTP_IDEMPOTENCY_KEY="k-3")
    assert res.status_code == 400
