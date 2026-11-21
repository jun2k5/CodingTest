from pathlib import Path

import pytest
from django.db import connection

ROOT = Path(__file__).resolve().parent.parent
TABLES = "review, order_item, orders, product, customer"


def apply_sql(name: str) -> None:
    with connection.cursor() as cur:
        cur.execute((ROOT / "sql" / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def django_db_setup(django_db_blocker):
    """pytest-django가 테스트 DB를 만들지 않게 하고, SQL 파일로 스키마를 만든다."""
    with django_db_blocker.unblock():
        apply_sql("001_schema.sql")


@pytest.fixture(autouse=True)
def clean_db(django_db_setup, django_db_blocker):
    """테스트마다 모든 테이블을 비운다(커밋된 데이터도 지운다)."""
    with django_db_blocker.unblock():
        with connection.cursor() as cur:
            cur.execute(f"TRUNCATE {TABLES} RESTART IDENTITY CASCADE")
            # 테스트가 만든 인덱스(이름이 _idx로 끝남)도 지운다. TRUNCATE는 인덱스를 남긴다.
            cur.execute("SELECT indexname FROM pg_indexes WHERE schemaname = 'public' "
                        r"AND indexname LIKE '%%\_idx'")
            for (name,) in cur.fetchall():
                cur.execute(f'DROP INDEX IF EXISTS "{name}"')
        yield


@pytest.fixture(params=["a", "b"])
def backend(request, settings):
    """같은 테스트를 방식 A와 B로 한 번씩 실행한다."""
    settings.SHOP_DB_BACKEND = request.param
    yield request.param


@pytest.fixture(scope="session", autouse=True)
def _close_pool():
    yield
    from shop_b.db import close_pool

    close_pool()


@pytest.fixture
def client():
    from rest_framework.test import APIClient

    return APIClient()


class ServerStats:
    """pg_stat_statements로 DB 서버가 실제로 받은 문장 수를 센다."""

    def reset(self) -> None:
        with connection.cursor() as cur:
            cur.execute("SELECT pg_stat_statements_reset()")

    def calls(self, like: str) -> int:
        with connection.cursor() as cur:
            cur.execute(
                "SELECT coalesce(sum(calls), 0) FROM pg_stat_statements "
                "WHERE query ILIKE %s AND query NOT ILIKE '%%pg_stat_statements%%'",
                [like],
            )
            return int(cur.fetchone()[0])


@pytest.fixture
def server_stats():
    return ServerStats()


def product_row(i: int, **over) -> dict:
    row = {"sku": f"SKU-{i:05d}", "name": f"상품 {i}", "category": "book", "price": 1000 + i, "stock": 10}
    row.update(over)
    return row


OUTPUTS = ROOT / "outputs"


def explain(sql: str, params=None, save_as: str | None = None) -> str:
    """EXPLAIN ANALYZE 결과를 문자열로 돌려준다. 시간·비용은 빼서 실행마다 같은 결과가 나온다.

    save_as를 주면 outputs/<save_as>.txt에 저장한다(글에 싣는 출력의 원본).
    """
    with connection.cursor() as cur:
        cur.execute("EXPLAIN (ANALYZE, COSTS OFF, TIMING OFF, SUMMARY OFF) " + sql, params)
        plan = "\n".join(r[0] for r in cur.fetchall())
    if save_as:
        OUTPUTS.mkdir(exist_ok=True)
        (OUTPUTS / f"{save_as}.txt").write_text(plan + "\n", encoding="utf-8")
    return plan


def buffers(sql: str, params=None) -> int:
    """EXPLAIN (ANALYZE, BUFFERS)의 최상위 노드가 읽은 공유 버퍼 수(hit + read)."""
    import json as _json

    with connection.cursor() as cur:
        cur.execute("EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) " + sql, params)
        raw = cur.fetchone()[0]
    plan = (raw if isinstance(raw, list) else _json.loads(raw))[0]["Plan"]
    return plan["Shared Hit Blocks"] + plan["Shared Read Blocks"]


def run_concurrently(*fns, timeout: float = 15.0) -> list:
    """함수들을 스레드에서 동시에 실행하고 [결과 또는 예외] 목록을 돌려준다.

    스레드마다 Django 연결이 따로 생기므로(방식 A) 끝날 때 닫는다.
    """
    import threading

    from django.db import connections

    results: list = [None] * len(fns)

    def worker(i, fn):
        try:
            results[i] = fn()
        except BaseException as exc:  # noqa: BLE001 - 테스트가 예외를 검사한다
            results[i] = exc
        finally:
            connections.close_all()

    threads = [threading.Thread(target=worker, args=(i, fn)) for i, fn in enumerate(fns)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout)
    return results
