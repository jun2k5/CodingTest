"""방식 B: psycopg_pool로 연결을 직접 관리한다. Django의 DB 계층은 쓰지 않는다."""
from contextlib import contextmanager
from contextvars import ContextVar

from django.conf import settings
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from core.querylog import record

_pool: ConnectionPool | None = None
# transaction() 블록 안에서는 같은 연결을 계속 써야 하므로 현재 연결을 기억한다.
_current = ContextVar("shop_b_conn", default=None)


def conninfo() -> str:
    d = settings.DB
    return (
        f"host={d['HOST']} port={d['PORT']} dbname={d['NAME']} "
        f"user={d['USER']} password={d['PASSWORD']}"
    )


def get_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        opts = settings.SHOP_B_POOL
        _pool = ConnectionPool(
            conninfo(),
            min_size=opts["min_size"],
            max_size=opts["max_size"],
            timeout=opts["timeout"],
            # autocommit=True: 블록 밖 단일 SQL은 바로 커밋되고(A와 같다), transaction()은 BEGIN/COMMIT을 직접 보낸다.
            # False(psycopg 기본)면 SQL마다 암묵적 BEGIN이 붙고, CREATE INDEX CONCURRENTLY·VACUUM이 실패한다.
            kwargs={"row_factory": dict_row, "autocommit": True},
            open=True,
        )
    return _pool


def close_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


@contextmanager
def _conn():
    conn = _current.get()
    if conn is not None:
        yield conn
        return
    # 블록 밖의 단일 호출: 연결을 빌려 실행하고 반납한다(autocommit이라 SQL마다 커밋).
    with get_pool().connection() as conn:
        yield conn


def fetch_all(sql: str, params=None) -> list[dict]:
    record(sql)
    with _conn() as conn:
        return conn.execute(sql, params).fetchall()


def fetch_one(sql: str, params=None) -> dict | None:
    rows = fetch_all(sql, params)
    return rows[0] if rows else None


def execute(sql: str, params=None) -> int:
    record(sql)
    with _conn() as conn:
        return conn.execute(sql, params).rowcount


def executemany(sql: str, seq) -> None:
    record(sql)
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.executemany(sql, seq)


@contextmanager
def transaction():
    """하나의 연결을 빌려 블록 전체를 한 트랜잭션으로 묶는다. 중첩되면 savepoint."""
    conn = _current.get()
    if conn is not None:
        with conn.transaction():
            yield
        return
    with get_pool().connection() as conn:
        token = _current.set(conn)
        try:
            with conn.transaction():
                yield
        finally:
            _current.reset(token)
