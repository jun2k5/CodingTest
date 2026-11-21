-- 001_schema.sql: 예제 쇼핑 도메인 스키마
-- FK 컬럼에는 일부러 인덱스를 만들지 않는다(05편에서 002_indexes.sql로 추가).
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

DROP TABLE IF EXISTS review, order_item, orders, product, customer CASCADE;

CREATE TABLE customer (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email       text        NOT NULL UNIQUE,
    name        text        NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE product (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sku         text        NOT NULL UNIQUE,
    name        text        NOT NULL,
    category    text        NOT NULL,
    price       integer     NOT NULL CHECK (price >= 0),
    stock       integer     NOT NULL CHECK (stock >= 0),
    version     integer     NOT NULL DEFAULT 1,
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE orders (
    id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id      bigint      NOT NULL REFERENCES customer (id),
    status           text        NOT NULL DEFAULT 'pending'
                     CHECK (status IN ('pending', 'paid', 'shipped', 'cancelled')),
    total            integer     NOT NULL DEFAULT 0,
    idempotency_key  text        UNIQUE,
    created_at       timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE order_item (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id    bigint  NOT NULL REFERENCES orders (id) ON DELETE CASCADE,
    product_id  bigint  NOT NULL REFERENCES product (id),
    quantity    integer NOT NULL CHECK (quantity > 0),
    unit_price  integer NOT NULL
);

CREATE TABLE review (
    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id   bigint      NOT NULL REFERENCES product (id) ON DELETE CASCADE,
    customer_id  bigint      NOT NULL REFERENCES customer (id),
    rating       smallint    NOT NULL CHECK (rating BETWEEN 1 AND 5),
    body         text        NOT NULL DEFAULT '',
    created_at   timestamptz NOT NULL DEFAULT now()
);
