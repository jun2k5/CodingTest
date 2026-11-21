"""상품 하나에 역참조가 둘(order_item, review)일 때의 집계와 상품별 최신 리뷰 N개."""
from core.db import get_db


def stats_naive_join(product_id: int) -> dict:
    """역참조 두 개를 한 번에 JOIN하면 행이 곱해져 개수가 부풀려진다(잘못된 예)."""
    return get_db().fetch_one(
        "SELECT count(r.id) AS reviews, coalesce(sum(i.quantity), 0) AS sold "
        "FROM product p "
        "LEFT JOIN review r ON r.product_id = p.id "
        "LEFT JOIN order_item i ON i.product_id = p.id "
        "WHERE p.id = %s",
        [product_id],
    )


def stats(product_id: int) -> dict:
    """역참조마다 따로 집계한 뒤 붙인다."""
    return get_db().fetch_one(
        "SELECT (SELECT count(*) FROM review r WHERE r.product_id = p.id) AS reviews, "
        "       (SELECT coalesce(sum(quantity), 0) FROM order_item i WHERE i.product_id = p.id) AS sold "
        "FROM product p WHERE p.id = %s",
        [product_id],
    )


def latest_reviews(product_ids: list[int], per_product: int) -> list[dict]:
    """상품마다 최신 리뷰 N개. 'id 목록 + IN'으로는 상품별 LIMIT을 걸 수 없어 LATERAL을 쓴다."""
    return get_db().fetch_all(
        "SELECT p.id AS product_id, r.id AS review_id, r.rating "
        "FROM unnest(%(ids)s::bigint[]) AS p(id) "
        "CROSS JOIN LATERAL ( "
        "   SELECT id, rating FROM review WHERE product_id = p.id "
        "   ORDER BY created_at DESC, id DESC LIMIT %(n)s "
        ") r ORDER BY p.id, r.id DESC",
        {"ids": product_ids, "n": per_product},
    )
