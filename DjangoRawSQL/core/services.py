"""09편: 트랜잭션 범위. 잠금을 잡은 채로 느린 일(외부 API 호출)을 하지 않는다."""
from core.db import get_db


def change_price_call_inside(product_id: int, price: int, external_call) -> None:
    """잘못된 예: 행을 잠근 채로 외부 호출을 기다린다."""
    db = get_db()
    with db.transaction():
        db.fetch_one("SELECT id FROM product WHERE id = %s FOR UPDATE", [product_id])
        external_call()
        db.execute("UPDATE product SET price = %s WHERE id = %s", [price, product_id])


def change_price_call_outside(product_id: int, price: int, external_call) -> None:
    """외부 호출을 먼저 끝내고, DB 변경만 짧은 트랜잭션으로."""
    external_call()
    db = get_db()
    with db.transaction():
        db.execute("UPDATE product SET price = %s WHERE id = %s", [price, product_id])
