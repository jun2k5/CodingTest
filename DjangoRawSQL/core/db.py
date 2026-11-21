"""설정(SHOP_DB_BACKEND)에 따라 방식 A 또는 B의 DB 모듈을 돌려준다.

두 모듈은 같은 함수(fetch_all, fetch_one, execute, executemany, transaction)를 가진다.
리포지토리 코드는 어느 방식인지 모른 채 이 인터페이스만 쓴다.
"""
from django.conf import settings


def get_db():
    if settings.SHOP_DB_BACKEND == "b":
        from shop_b import db
    else:
        from shop_a import db
    return db
