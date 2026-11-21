"""방식 A: Django가 관리하는 연결에서 SQL을 직접 실행한다(ORM은 쓰지 않는다)."""
from django.db import connection
from django.db import transaction as dj_transaction

from core.querylog import record


def _rows(cursor) -> list[dict]:
    if cursor.description is None:
        return []
    cols = [c.name for c in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def fetch_all(sql: str, params=None) -> list[dict]:
    record(sql)
    with connection.cursor() as cur:
        cur.execute(sql, params)
        return _rows(cur)


def fetch_one(sql: str, params=None) -> dict | None:
    rows = fetch_all(sql, params)
    return rows[0] if rows else None


def execute(sql: str, params=None) -> int:
    """INSERT/UPDATE/DELETE를 실행하고 영향받은 행 수를 돌려준다."""
    record(sql)
    with connection.cursor() as cur:
        cur.execute(sql, params)
        return cur.rowcount


def executemany(sql: str, seq) -> None:
    record(sql)
    with connection.cursor() as cur:
        cur.executemany(sql, seq)


def transaction():
    """Django의 atomic을 그대로 쓴다. 중첩되면 savepoint가 된다."""
    return dj_transaction.atomic()
