"""상품 리포지토리. ORM 없이 SQL만 쓴다. 어느 방식(A·B)인지는 get_db()가 정한다."""
from core.db import get_db

COLUMNS = "id, sku, name, category, price, stock, version, created_at, updated_at"
# PATCH로 바꿀 수 있는 컬럼. SQL에 넣는 컬럼 이름은 반드시 이 목록에서만 가져온다.
UPDATABLE = ("name", "category", "price", "stock")


def create(data: dict) -> dict:
    return get_db().fetch_one(
        "INSERT INTO product (sku, name, category, price, stock) "
        "VALUES (%(sku)s, %(name)s, %(category)s, %(price)s, %(stock)s) "
        f"RETURNING {COLUMNS}",
        data,
    )


def get(product_id: int) -> dict | None:
    return get_db().fetch_one(f"SELECT {COLUMNS} FROM product WHERE id = %s", [product_id])


def update(product_id: int, fields: dict) -> dict | None:
    """바뀐 필드만 SET에 넣는다. 값은 파라미터로, 컬럼 이름은 화이트리스트로."""
    unknown = set(fields) - set(UPDATABLE)
    if unknown or not fields:
        raise ValueError(f"수정할 수 없는 필드: {sorted(unknown)}" if unknown else "수정할 필드가 없다")
    sets = ", ".join(f"{col} = %({col})s" for col in UPDATABLE if col in fields)
    return get_db().fetch_one(
        f"UPDATE product SET {sets}, version = version + 1, updated_at = now() "
        f"WHERE id = %(id)s RETURNING {COLUMNS}",
        {**fields, "id": product_id},
    )


def delete(product_id: int) -> bool:
    return get_db().execute("DELETE FROM product WHERE id = %s", [product_id]) == 1


def bulk_create_executemany(rows: list[dict]) -> None:
    """행마다 INSERT 문을 한 번씩 보낸다."""
    get_db().executemany(
        "INSERT INTO product (sku, name, category, price, stock) "
        "VALUES (%(sku)s, %(name)s, %(category)s, %(price)s, %(stock)s)",
        rows,
    )


def bulk_create(rows: list[dict]) -> int:
    """열마다 배열 하나를 넘기고 unnest로 펼쳐 INSERT 한 번에 넣는다."""
    cols = ("sku", "name", "category", "price", "stock")
    arrays = [[r[c] for r in rows] for c in cols]
    return get_db().execute(
        "INSERT INTO product (sku, name, category, price, stock) "
        "SELECT * FROM unnest(%s::text[], %s::text[], %s::text[], %s::int[], %s::int[])",
        arrays,
    )
