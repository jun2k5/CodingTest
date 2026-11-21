"""두 방식(A·B)이 실행한 SQL을 같은 방법으로 세기 위한 기록기."""
from contextlib import contextmanager
from contextvars import ContextVar

_log: ContextVar[list | None] = ContextVar("querylog", default=None)


def record(sql: str) -> None:
    log = _log.get()
    if log is not None:
        log.append(" ".join(sql.split()))


@contextmanager
def capture():
    """with capture() as queries: ... 블록 안에서 실행된 SQL 목록을 모은다."""
    queries: list[str] = []
    token = _log.set(queries)
    try:
        yield queries
    finally:
        _log.reset(token)
