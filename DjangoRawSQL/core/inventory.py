"""07편: API 안에서 생기는 동시성 문제와 해결 방법(재고 차감, 낙관적 잠금, 주문 생성)."""
from core.db import get_db
from core.errors import VersionConflict
from core.products import COLUMNS, UPDATABLE


class OutOfStock(Exception):
    pass


def reserve_read_then_write(product_id: int, qty: int, between=None) -> int:
    """잘못된 예: 읽고, 파이썬에서 계산하고, 결과를 덮어쓴다(갱신 손실)."""
    db = get_db()
    stock = db.fetch_one("SELECT stock FROM product WHERE id = %s", [product_id])["stock"]
    if between:
        between()           # 테스트가 두 요청을 이 지점에서 겹치게 만든다
    if stock < qty:
        raise OutOfStock
    db.execute("UPDATE product SET stock = %s WHERE id = %s", [stock - qty, product_id])
    return stock - qty


def reserve_atomic(product_id: int, qty: int) -> int:
    """조건과 계산을 UPDATE 한 문장에 넣는다. 행 잠금 안에서 최신 값으로 다시 평가된다."""
    row = get_db().fetch_one(
        "UPDATE product SET stock = stock - %(qty)s, version = version + 1, updated_at = now() "
        "WHERE id = %(id)s AND stock >= %(qty)s RETURNING stock",
        {"id": product_id, "qty": qty},
    )
    if row is None:
        raise OutOfStock
    return row["stock"]


def reserve_for_update(product_id: int, qty: int, between=None) -> int:
    """판단 로직이 길어 한 문장에 못 넣을 때: 먼저 행을 잠그고 읽는다."""
    db = get_db()
    with db.transaction():
        stock = db.fetch_one(
            "SELECT stock FROM product WHERE id = %s FOR UPDATE", [product_id]
        )["stock"]
        if between:
            between()
        if stock < qty:
            raise OutOfStock
        db.execute("UPDATE product SET stock = %s WHERE id = %s", [stock - qty, product_id])
        return stock - qty


def update_if_version(product_id: int, fields: dict, expected_version: int) -> dict | None:
    """낙관적 잠금: 읽은 version과 같을 때만 고친다. 다르면 VersionConflict, 행이 없으면 None."""
    unknown = set(fields) - set(UPDATABLE)
    if unknown or not fields:
        raise ValueError("수정할 수 없는 필드")
    db = get_db()
    sets = ", ".join(f"{c} = %({c})s" for c in UPDATABLE if c in fields)
    row = db.fetch_one(
        f"UPDATE product SET {sets}, version = version + 1, updated_at = now() "
        f"WHERE id = %(id)s AND version = %(v)s RETURNING {COLUMNS}",
        {**fields, "id": product_id, "v": expected_version},
    )
    if row is not None:
        return row
    if db.fetch_one("SELECT 1 AS x FROM product WHERE id = %s", [product_id]) is None:
        return None
    raise VersionConflict


def place_order(customer_id: int, items: list[tuple[int, int]], lock_sorted: bool = True,
                between=None) -> int:
    """주문 생성: 재고 차감 + 주문·항목 INSERT를 한 트랜잭션으로.

    여러 상품을 잠글 때 항상 id 순서로 잠그면 교착 상태(deadlock)가 생기지 않는다.
    """
    db = get_db()
    ordered = sorted(items) if lock_sorted else list(items)
    with db.transaction():
        total = 0
        for i, (pid, qty) in enumerate(ordered):
            row = db.fetch_one(
                "UPDATE product SET stock = stock - %(qty)s WHERE id = %(id)s AND stock >= %(qty)s "
                "RETURNING price",
                {"id": pid, "qty": qty},
            )
            if row is None:
                raise OutOfStock(pid)
            total += row["price"] * qty
            if between and i == 0:
                between()
        order = db.fetch_one(
            "INSERT INTO orders (customer_id, total) VALUES (%s, %s) RETURNING id", [customer_id, total]
        )
        db.execute(
            "INSERT INTO order_item (order_id, product_id, quantity, unit_price) "
            "SELECT %s, p.id, x.qty, p.price FROM unnest(%s::bigint[], %s::int[]) AS x(pid, qty) "
            "JOIN product p ON p.id = x.pid",
            [order["id"], [p for p, _ in ordered], [q for _, q in ordered]],
        )
        return order["id"]
