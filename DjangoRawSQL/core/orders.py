"""주문 목록: 정참조(orders → customer)와 역참조(orders ← order_item)를 SQL로 가져오는 네 가지 방법.

모두 같은 모양을 돌려준다.
[{"id", "status", "customer": {"id", "name"}, "items": [{"product_id", "quantity", "unit_price"}]}]
"""
import json

from core.db import get_db

ORDER_PAGE = "SELECT id, customer_id, status FROM orders ORDER BY id LIMIT %(limit)s"


def _shape(order: dict, customer: dict, items: list[dict]) -> dict:
    return {"id": order["id"], "status": order["status"],
            "customer": {"id": customer["id"], "name": customer["name"]},
            "items": [{"product_id": i["product_id"], "quantity": i["quantity"],
                       "unit_price": i["unit_price"]} for i in items]}


def list_n_plus_1(limit: int) -> list[dict]:
    """주문 1번 + 주문마다 고객 1번 + 주문마다 항목 1번 = 1 + 2N 쿼리."""
    db = get_db()
    result = []
    for o in db.fetch_all(ORDER_PAGE, {"limit": limit}):
        c = db.fetch_one("SELECT id, name FROM customer WHERE id = %s", [o["customer_id"]])
        items = db.fetch_all(
            "SELECT product_id, quantity, unit_price FROM order_item WHERE order_id = %s ORDER BY id",
            [o["id"]],
        )
        result.append(_shape(o, c, items))
    return result


def list_flat_join(limit: int) -> list[dict]:
    """한 번의 JOIN. 주문 × 항목 수만큼 행이 늘어나 파이썬에서 다시 묶는다.

    주의: LIMIT이 '주문'이 아니라 '행'에 걸린다(테스트로 확인).
    """
    rows = get_db().fetch_all(
        "SELECT o.id, o.status, c.id AS customer_id, c.name, "
        "       i.product_id, i.quantity, i.unit_price "
        "FROM orders o JOIN customer c ON c.id = o.customer_id "
        "LEFT JOIN order_item i ON i.order_id = o.id "
        "ORDER BY o.id, i.id LIMIT %(limit)s",
        {"limit": limit},
    )
    grouped: dict[int, dict] = {}
    for r in rows:
        o = grouped.setdefault(r["id"], _shape(r, {"id": r["customer_id"], "name": r["name"]}, []))
        if r["product_id"] is not None:
            o["items"].append({"product_id": r["product_id"], "quantity": r["quantity"],
                               "unit_price": r["unit_price"]})
    return list(grouped.values())


def list_two_queries(limit: int) -> list[dict]:
    """정참조는 JOIN으로 붙이고, 역참조는 id 목록으로 한 번 더 가져온다 = 2 쿼리."""
    db = get_db()
    orders = db.fetch_all(
        "SELECT o.id, o.status, c.id AS customer_id, c.name "
        "FROM orders o JOIN customer c ON c.id = o.customer_id ORDER BY o.id LIMIT %(limit)s",
        {"limit": limit},
    )
    ids = [o["id"] for o in orders]
    by_order: dict[int, list[dict]] = {i: [] for i in ids}
    for it in db.fetch_all(
        "SELECT order_id, product_id, quantity, unit_price FROM order_item "
        "WHERE order_id = ANY(%s) ORDER BY id",
        [ids],
    ):
        by_order[it["order_id"]].append(it)
    return [_shape(o, {"id": o["customer_id"], "name": o["name"]}, by_order[o["id"]]) for o in orders]


def list_json_agg(limit: int) -> list[dict]:
    """주문마다 항목을 JSON 배열로 묶어 1 쿼리로 끝낸다."""
    rows = get_db().fetch_all(
        "SELECT o.id, o.status, c.id AS customer_id, c.name, "
        "       COALESCE(items.list, '[]'::json) AS items "
        "FROM (SELECT id, customer_id, status FROM orders ORDER BY id LIMIT %(limit)s) o "
        "JOIN customer c ON c.id = o.customer_id "
        "LEFT JOIN LATERAL ( "
        "   SELECT json_agg(json_build_object('product_id', i.product_id, "
        "          'quantity', i.quantity, 'unit_price', i.unit_price) ORDER BY i.id) AS list "
        "   FROM order_item i WHERE i.order_id = o.id "
        ") items ON true "
        "ORDER BY o.id",
        {"limit": limit},
    )
    out = []
    for r in rows:
        items = r["items"] if not isinstance(r["items"], str) else json.loads(r["items"])
        out.append(_shape(r, {"id": r["customer_id"], "name": r["name"]}, items))
    return out
