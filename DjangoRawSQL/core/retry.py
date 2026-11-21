"""직렬화 실패(40001)와 교착 상태(40P01)는 트랜잭션 전체를 다시 실행하면 성공할 수 있다."""
import random
import time

RETRYABLE = {"40001", "40P01"}


def sqlstate(exc: BaseException | None) -> str | None:
    if exc is None:
        return None
    for e in (exc, exc.__cause__):
        if getattr(e, "sqlstate", None):
            return e.sqlstate
    return None


def run_with_retry(fn, attempts: int = 3, base_delay: float = 0.05):
    """fn은 트랜잭션 하나를 처음부터 끝까지 실행하는 함수여야 한다(부분 재시도 금지)."""
    for i in range(attempts):
        try:
            return fn()
        except Exception as exc:
            if sqlstate(exc) not in RETRYABLE or i == attempts - 1:
                raise
            time.sleep(base_delay * (2 ** i) * (1 + random.random()))
