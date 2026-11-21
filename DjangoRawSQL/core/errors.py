"""DB 제약 위반을 방식과 상관없이 같은 이름으로 분류한다.

방식 A는 Django가 psycopg 예외를 django.db.IntegrityError로 감싸고(__cause__에 원래 예외),
방식 B는 psycopg 예외가 그대로 올라온다. 둘 다 SQLSTATE로 구분한다.
"""
SQLSTATE = {"23505": "unique", "23503": "foreign_key", "23514": "check", "23502": "not_null"}


class NotFound(Exception):
    pass


class VersionConflict(Exception):
    """낙관적 잠금: 읽은 뒤 다른 요청이 먼저 고쳤다."""


def constraint_kind(exc: BaseException) -> str | None:
    for e in (exc, exc.__cause__):
        state = getattr(e, "sqlstate", None)
        if state in SQLSTATE:
            return SQLSTATE[state]
    return None
