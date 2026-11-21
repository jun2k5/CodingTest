"""상품 목록 조회: 필터·정렬 화이트리스트, OFFSET과 keyset 페이지네이션."""
import base64
import json

from core.db import get_db
from core.products import COLUMNS

# 요청 값 → (정렬 컬럼, 방향). SQL에 들어가는 이름은 이 표에서만 나온다.
SORTS = {
    "price": ("price", "ASC"),
    "-price": ("price", "DESC"),
    "created_at": ("created_at", "ASC"),
    "-created_at": ("created_at", "DESC"),
    "id": ("id", "ASC"),
}
FILTERS = {
    "category": "category = %(category)s",
    "min_price": "price >= %(min_price)s",
    "max_price": "price <= %(max_price)s",
}


def where_clause(filters: dict) -> str:
    unknown = set(filters) - set(FILTERS)
    if unknown:
        raise ValueError(f"알 수 없는 필터: {sorted(unknown)}")
    conds = [FILTERS[k] for k in FILTERS if k in filters]
    return ("WHERE " + " AND ".join(conds)) if conds else ""


def _sort(sort: str) -> tuple[str, str]:
    if sort not in SORTS:
        raise ValueError(f"알 수 없는 정렬: {sort}")
    return SORTS[sort]


def list_offset(filters: dict, sort: str = "id", page: int = 1, size: int = 20) -> list[dict]:
    col, direction = _sort(sort)
    return get_db().fetch_all(
        f"SELECT {COLUMNS} FROM product {where_clause(filters)} "
        f"ORDER BY {col} {direction}, id {direction} LIMIT %(limit)s OFFSET %(offset)s",
        {**filters, "limit": size, "offset": (page - 1) * size},
    )


def encode_cursor(row: dict, col: str) -> str:
    value = row[col]
    value = value.isoformat() if hasattr(value, "isoformat") else value
    return base64.urlsafe_b64encode(json.dumps([value, row["id"]]).encode()).decode()


def decode_cursor(cursor: str) -> list:
    try:
        value, last_id = json.loads(base64.urlsafe_b64decode(cursor.encode()))
        return [value, int(last_id)]
    except (ValueError, TypeError) as e:
        raise ValueError("잘못된 cursor") from e


def list_keyset(filters: dict, sort: str = "id", after: str | None = None,
                size: int = 20) -> tuple[list[dict], str | None]:
    """마지막으로 본 (정렬값, id) 다음부터 size개. 정렬값이 같아도 id로 순서가 정해진다.

    size + 1개를 읽어서 다음 페이지가 있는지 판단한다(COUNT를 쓰지 않는다).
    """
    col, direction = _sort(sort)
    where = where_clause(filters)
    params = {**filters, "limit": size + 1}
    if after is not None:
        params["after_value"], params["after_id"] = decode_cursor(after)
        op = ">" if direction == "ASC" else "<"
        cond = f"({col}, id) {op} (%(after_value)s, %(after_id)s)"
        where = f"{where} AND {cond}" if where else f"WHERE {cond}"
    rows = get_db().fetch_all(
        f"SELECT {COLUMNS} FROM product {where} "
        f"ORDER BY {col} {direction}, id {direction} LIMIT %(limit)s",
        params,
    )
    has_next = len(rows) > size
    rows = rows[:size]
    return rows, (encode_cursor(rows[-1], col) if has_next and rows else None)


def count(filters: dict) -> int:
    return get_db().fetch_one(
        f"SELECT count(*) AS n FROM product {where_clause(filters)}", filters
    )["n"]
