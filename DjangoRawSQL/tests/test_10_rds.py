"""10편: RDS 특성 중 로컬에서 흉내 낼 수 있는 것 - 왕복 지연, prepared statement, SSL 강제."""
import statistics
import time

import psycopg
import pytest
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from core import orders
from core.db import get_db
from shop_b import db as b_db
from tests.seed import seed_customers_orders, seed_products
from tools.latency_proxy import start_in_thread

PROXY_PORT, DELAY_MS = 54331, 5.0   # 한 방향 5ms → 왕복 약 10ms


@pytest.fixture(scope="module")
def proxy():
    start_in_thread(PROXY_PORT, 54329, DELAY_MS)
    return PROXY_PORT


@pytest.fixture
def remote_b(proxy, settings, monkeypatch):
    """방식 B의 풀을 지연 프록시를 거치는 연결로 바꾼다."""
    settings.SHOP_DB_BACKEND = "b"
    info = b_db.conninfo().replace("host=localhost", "host=127.0.0.1").replace("port=54329", f"port={proxy}")
    pool = ConnectionPool(info, min_size=1, max_size=2, open=True,
                          kwargs={"row_factory": dict_row, "autocommit": True})
    monkeypatch.setattr(b_db, "_pool", pool)
    yield
    pool.close()


def rtt_ms() -> float:
    db = get_db()
    samples = []
    for _ in range(10):
        t = time.perf_counter()
        db.fetch_one("SELECT 1 AS x")
        samples.append((time.perf_counter() - t) * 1000)
    return statistics.median(samples)


def elapsed_ms(fn) -> float:
    t = time.perf_counter()
    fn()
    return (time.perf_counter() - t) * 1000


def test_proxy_adds_round_trip_latency(remote_b):
    assert rtt_ms() >= 2 * DELAY_MS * 0.9


def test_n_plus_1_cost_scales_with_round_trips(remote_b):
    seed_products(50)
    seed_customers_orders(customers=5, orders_per_customer=4, items_per_order=3)   # 주문 20개
    rtt = rtt_ms()
    n_plus_1 = elapsed_ms(lambda: orders.list_n_plus_1(20))      # 41번 왕복
    two = elapsed_ms(lambda: orders.list_two_queries(20))        # 2번 왕복
    agg = elapsed_ms(lambda: orders.list_json_agg(20))           # 1번 왕복
    assert n_plus_1 >= 41 * rtt * 0.9
    assert two < 4 * rtt and agg < 3 * rtt


def test_psycopg_prepares_repeated_statements_server_side(settings):
    settings.SHOP_DB_BACKEND = "b"
    db = get_db()
    with db.transaction():                       # 같은 연결에서 6번
        for i in range(6):
            db.fetch_one("SELECT %s::int AS x", [i])
        prepared = db.fetch_one("SELECT count(*) AS n FROM pg_prepared_statements")["n"]
    assert prepared >= 1                         # prepare_threshold(기본 5)를 넘으면 서버에 준비해 둔다


def test_django_client_side_cursor_does_not_prepare(settings):
    settings.SHOP_DB_BACKEND = "a"
    db = get_db()
    with db.transaction():
        for i in range(6):
            db.fetch_one("SELECT %s::int AS x", [i])
        prepared = db.fetch_one("SELECT count(*) AS n FROM pg_prepared_statements")["n"]
    assert prepared == 0


def test_sslmode_require_fails_on_server_without_ssl():
    with pytest.raises(psycopg.OperationalError, match="SSL"):
        psycopg.connect(b_db.conninfo() + " sslmode=require", connect_timeout=3)
