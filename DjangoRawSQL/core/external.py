"""08편: API 바깥(ETL 배치, 다른 시스템)의 쓰기와 함께 쓰는 DB에서의 동시성 처리."""
from core.db import get_db
from core.errors import VersionConflict
from core.inventory import OutOfStock


TIMEOUTS = ("lock_timeout", "statement_timeout")


def set_local_timeout(name: str, ms: int) -> None:
    """SET LOCAL은 파라미터를 받지 못한다(SET lock_timeout = $1 불가).

    이름은 허용 목록에서, 값은 int로 바꾼 뒤 SQL에 직접 쓴다(사용자 입력이 아니다).
    set_config(name, value, true)도 같은 일을 하지만 RDS Proxy에서는 연결 고정(pinning)을 일으킨다.
    """
    if name not in TIMEOUTS:
        raise ValueError(name)
    get_db().execute(f"SET LOCAL {name} = {int(ms)}")   # 정수는 밀리초


def update_price_with_lock_timeout(product_id: int, price: int, timeout_ms: int = 200) -> dict | None:
    """행 잠금을 timeout_ms까지만 기다린다. 넘으면 55P03(lock_not_available). 0은 무한 대기."""
    db = get_db()
    with db.transaction():
        set_local_timeout("lock_timeout", timeout_ms)
        return db.fetch_one(
            "UPDATE product SET price = %s, updated_at = now() WHERE id = %s RETURNING id, price",
            [price, product_id],
        )


def reserve_nowait(product_id: int, qty: int) -> int:
    """잠겨 있으면 기다리지 않고 바로 55P03."""
    db = get_db()
    with db.transaction():
        row = db.fetch_one("SELECT stock FROM product WHERE id = %s FOR UPDATE NOWAIT", [product_id])
        if row["stock"] < qty:
            raise OutOfStock
        return db.fetch_one(
            "UPDATE product SET stock = stock - %s WHERE id = %s RETURNING stock", [qty, product_id]
        )["stock"]


def run_with_statement_timeout(sql: str, timeout_ms: int = 100) -> list[dict]:
    db = get_db()
    with db.transaction():
        set_local_timeout("statement_timeout", timeout_ms)
        return db.fetch_all(sql)


def claim_pending_orders(limit: int) -> list[int]:
    """작업자 여러 개가 처리 대기 주문을 나눠 가진다. 다른 작업자가 잠근 행은 건너뛴다."""
    rows = get_db().fetch_all(
        "UPDATE orders SET status = 'paid' WHERE id IN ( "
        "   SELECT id FROM orders WHERE status = 'pending' ORDER BY id LIMIT %s "
        "   FOR UPDATE SKIP LOCKED "
        ") RETURNING id",
        [limit],
    )
    return sorted(r["id"] for r in rows)


def etl_upsert(rows: list[dict]) -> int:
    """sku 기준 upsert. 이미 더 최근에 고친 행(updated_at이 더 큼)은 덮어쓰지 않는다."""
    cols = ("sku", "name", "category", "price", "stock", "updated_at")
    return get_db().execute(
        "INSERT INTO product (sku, name, category, price, stock, updated_at) "
        "SELECT * FROM unnest(%s::text[], %s::text[], %s::text[], %s::int[], %s::int[], %s::timestamptz[]) "
        "ON CONFLICT (sku) DO UPDATE SET name = EXCLUDED.name, price = EXCLUDED.price, "
        "    stock = EXCLUDED.stock, updated_at = EXCLUDED.updated_at "
        "WHERE product.updated_at < EXCLUDED.updated_at",
        [[r[c] for r in rows] for c in cols],
    )


def get_with_xmin(product_id: int) -> dict | None:
    """xmin: 그 행을 마지막으로 쓴 트랜잭션 id. 누가 어떤 경로로 고치든 바뀐다."""
    return get_db().fetch_one(
        "SELECT id, price, version, xmin::text AS row_version FROM product WHERE id = %s", [product_id]
    )


def update_price_if_xmin(product_id: int, price: int, row_version: str) -> dict:
    db = get_db()
    row = db.fetch_one(
        "UPDATE product SET price = %s, updated_at = now() "
        "WHERE id = %s AND xmin = %s::xid RETURNING id, price, xmin::text AS row_version",
        [price, product_id, row_version],
    )
    if row is None:
        raise VersionConflict
    return row


def create_order_idempotent(key: str, customer_id: int, product_id: int, qty: int) -> tuple[int, bool]:
    """같은 Idempotency-Key로 몇 번 와도 주문은 하나. (주문 id, 새로 만들었는가)."""
    db = get_db()
    with db.transaction():
        row = db.fetch_one(
            "INSERT INTO orders (customer_id, idempotency_key) VALUES (%s, %s) "
            "ON CONFLICT (idempotency_key) DO NOTHING RETURNING id",
            [customer_id, key],
        )
        if row is None:   # 이미 처리한 요청: 같은 결과를 돌려준다
            return db.fetch_one("SELECT id FROM orders WHERE idempotency_key = %s", [key])["id"], False
        price = db.fetch_one(
            "UPDATE product SET stock = stock - %(q)s WHERE id = %(p)s AND stock >= %(q)s RETURNING price",
            {"p": product_id, "q": qty},
        )
        if price is None:
            raise OutOfStock(product_id)   # 트랜잭션이 롤백되어 키도 남지 않는다
        db.execute(
            "INSERT INTO order_item (order_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)",
            [row["id"], product_id, qty, price["price"]],
        )
        db.execute("UPDATE orders SET total = %s WHERE id = %s", [price["price"] * qty, row["id"]])
        return row["id"], True
