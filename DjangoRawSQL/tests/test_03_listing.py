"""03편: 목록 조회 - 정렬·필터 화이트리스트, OFFSET과 keyset, COUNT 비용."""
import pytest
from django.db import ProgrammingError

from core import listing, products
from core.db import get_db
from tests.conftest import explain, product_row
from tests.seed import run, seed_products

URL = "/api/products/"


def test_sort_must_be_whitelisted(backend, client):
    res = client.get(URL, {"sort": "price; DROP TABLE product"})
    assert res.status_code == 400


def test_order_by_placeholder_a_client_binding_raises(settings):
    settings.SHOP_DB_BACKEND = "a"
    # Django는 기본으로 클라이언트 측 바인딩: ORDER BY 'price' 문자열 상수가 되어 오류
    with pytest.raises(ProgrammingError, match="non-integer constant in ORDER BY"):
        get_db().fetch_all("SELECT price FROM product ORDER BY %s", ["price"])


def test_order_by_placeholder_b_server_binding_silently_not_sorted(settings):
    settings.SHOP_DB_BACKEND = "b"
    for i, price in enumerate([3000, 1000, 2000]):
        products.create(product_row(i, price=price))
    # psycopg 기본은 서버 측 바인딩: ORDER BY $1 은 오류 없이 상수로 정렬(=정렬 안 됨)
    rows = get_db().fetch_all("SELECT price FROM product ORDER BY %s", ["price"])
    assert [r["price"] for r in rows] != [1000, 2000, 3000]


def test_keyset_covers_all_rows_with_duplicate_sort_values(backend):
    products.bulk_create([product_row(i, price=(i % 4) * 100) for i in range(103)])
    seen, cursor = [], None
    while True:
        rows, cursor = listing.list_keyset({}, "-price", cursor, size=10)
        seen += [r["id"] for r in rows]
        if cursor is None:
            break
    assert len(seen) == 103 and len(set(seen)) == 103


def test_offset_repeats_row_when_new_row_inserted(backend):
    products.bulk_create([product_row(i) for i in range(30)])
    page1 = listing.list_offset({}, "-created_at", page=1, size=10)
    products.create(product_row(999))  # 1페이지를 본 뒤 맨 앞에 새 행이 생긴다
    page2 = listing.list_offset({}, "-created_at", page=2, size=10)
    assert page2[0]["id"] == page1[-1]["id"]  # 같은 행이 두 페이지에 나온다


def test_keyset_does_not_repeat_when_new_row_inserted(backend):
    products.bulk_create([product_row(i) for i in range(30)])
    page1, cursor = listing.list_keyset({}, "-created_at", None, size=10)
    products.create(product_row(999))
    page2, _ = listing.list_keyset({}, "-created_at", cursor, size=10)
    assert not {r["id"] for r in page1} & {r["id"] for r in page2}


def test_next_cursor_without_count(backend, client):
    products.bulk_create([product_row(i) for i in range(40)])
    first = client.get(URL, {"size": 20}).json()
    second = client.get(URL, {"size": 20, "cursor": first["next"]}).json()
    assert len(first["results"]) == 20 and first["next"] is not None
    assert len(second["results"]) == 20 and second["next"] is None


def test_filter_must_be_whitelisted(backend):
    try:
        listing.list_keyset({"name; --": "x"})
    except ValueError:
        return
    raise AssertionError("모르는 필터는 거부해야 한다")


def test_explain_deep_offset_vs_keyset():
    seed_products(100_000)
    run("CREATE INDEX product_price_id_idx ON product (price, id)")
    run("ANALYZE product")
    offset_plan = explain(
        "SELECT id, price FROM product ORDER BY price, id LIMIT 20 OFFSET 90000",
        save_as="03_offset",
    )
    keyset_plan = explain(
        "SELECT id, price FROM product WHERE (price, id) > (45000, 0) ORDER BY price, id LIMIT 20",
        save_as="03_keyset",
    )
    assert "rows=90020" in offset_plan      # 버릴 9만 행까지 읽는다
    assert "rows=20 " in keyset_plan.splitlines()[1] + " "


def test_explain_count_reads_every_matching_row():
    seed_products(100_000)
    plan = explain("SELECT count(*) FROM product WHERE category = 'book'", save_as="03_count")
    assert "rows=20000" in plan
