-- 002_indexes.sql: 05편에서 근거를 확인한 인덱스
-- FK 컬럼(역참조 조회용). PostgreSQL은 FK 제약을 만들어도 이 인덱스를 자동으로 만들지 않는다.
CREATE INDEX IF NOT EXISTS order_item_order_id_idx   ON order_item (order_id);
CREATE INDEX IF NOT EXISTS order_item_product_id_idx ON order_item (product_id);
CREATE INDEX IF NOT EXISTS review_customer_id_idx    ON review (customer_id);

-- "고객의 최근 주문": 등호 조건 컬럼 먼저, 정렬 컬럼 다음
CREATE INDEX IF NOT EXISTS orders_customer_created_idx ON orders (customer_id, created_at DESC);

-- "상품의 최신 리뷰 N개"(04편 LATERAL)
CREATE INDEX IF NOT EXISTS review_product_created_idx ON review (product_id, created_at DESC, id DESC);

-- 목록 keyset(03편)
CREATE INDEX IF NOT EXISTS product_price_id_idx ON product (price, id);

-- 처리 대기 주문만: 부분 인덱스
CREATE INDEX IF NOT EXISTS orders_pending_created_idx ON orders (created_at) WHERE status = 'pending';
