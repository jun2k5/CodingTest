"""02편: SQL로 짜는 CRUD. 같은 API를 방식 A·B로 각각 확인한다."""
from core import products
from tests.conftest import product_row

URL = "/api/products/"


def test_create_returns_201_with_db_generated_columns(backend, client):
    res = client.post(URL, product_row(1), format="json")
    assert res.status_code == 201
    body = res.json()
    assert body["id"] == 1 and body["version"] == 1
    assert body["created_at"] is not None  # RETURNING으로 DB가 만든 값까지 한 번에 받는다


def test_get_missing_returns_404(backend, client):
    assert client.get(f"{URL}999/").status_code == 404


def test_patch_updates_only_given_fields(backend, client):
    pid = client.post(URL, product_row(1), format="json").json()["id"]
    before = client.get(f"{URL}{pid}/").json()
    res = client.patch(f"{URL}{pid}/", {"price": 9900}, format="json")
    after = res.json()
    assert res.status_code == 200
    assert after["price"] == 9900 and after["name"] == before["name"]
    assert after["version"] == 2 and after["updated_at"] > before["updated_at"]


def test_patch_rejects_unknown_field(backend, client):
    pid = client.post(URL, product_row(1), format="json").json()["id"]
    res = client.patch(f"{URL}{pid}/", {"stok": 5}, format="json")
    assert res.status_code == 400 and "stok" in res.json()


def test_patch_rejects_sql_in_field_name(backend):
    products.create(product_row(1))
    try:
        products.update(1, {"price = 0, stock": 1})
    except ValueError as e:
        assert "수정할 수 없는 필드" in str(e)
    else:
        raise AssertionError("컬럼 이름은 화이트리스트 밖이면 거부해야 한다")
    assert products.get(1)["price"] == 1001


def test_patch_rejects_empty_body(backend, client):
    pid = client.post(URL, product_row(1), format="json").json()["id"]
    assert client.patch(f"{URL}{pid}/", {}, format="json").status_code == 400


def test_duplicate_sku_returns_409(backend, client):
    client.post(URL, product_row(1), format="json")
    res = client.post(URL, product_row(1), format="json")
    assert res.status_code == 409 and res.json() == {"error": "unique"}


def test_value_is_parameter_not_sql(backend, client):
    evil = product_row(1, name="x'); DROP TABLE product; --")
    res = client.post(URL, evil, format="json")
    assert res.status_code == 201
    assert products.get(res.json()["id"])["name"] == evil["name"]


def test_delete_returns_204_then_404(backend, client):
    pid = client.post(URL, product_row(1), format="json").json()["id"]
    assert client.delete(f"{URL}{pid}/").status_code == 204
    assert client.delete(f"{URL}{pid}/").status_code == 404


def test_bulk_insert_server_statement_count(backend, server_stats):
    rows = [product_row(i) for i in range(1000)]
    server_stats.reset()
    products.bulk_create_executemany(rows)
    many = server_stats.calls("INSERT INTO product%")
    server_stats.reset()
    products.bulk_create([product_row(i, sku=f"U-{i}") for i in range(1000)])
    unnest = server_stats.calls("INSERT INTO product%")
    assert (many, unnest) == (1000, 1)
