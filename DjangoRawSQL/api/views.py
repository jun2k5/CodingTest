from django.db import DatabaseError as DjangoDatabaseError
from psycopg import Error as PsycopgError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core import external, inventory, listing, products
from core.errors import VersionConflict, constraint_kind

from .serializers import ProductIn, ProductPatch

DB_ERRORS = (DjangoDatabaseError, PsycopgError)
CONSTRAINT_STATUS = {"unique": 409, "foreign_key": 409, "check": 400, "not_null": 400}


def db_error_response(exc):
    kind = constraint_kind(exc)
    if kind is None:
        raise exc
    return Response({"error": kind}, status=CONSTRAINT_STATUS[kind])


class ProductListView(APIView):
    def get(self, request):
        q = request.query_params
        filters = {k: q[k] for k in listing.FILTERS if k in q}
        try:
            for k in ("min_price", "max_price"):
                if k in filters:
                    filters[k] = int(filters[k])
            size = min(int(q.get("size", 20)), 100)
            rows, nxt = listing.list_keyset(filters, q.get("sort", "id"), q.get("cursor"), size)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"results": rows, "next": nxt})

    def post(self, request):
        s = ProductIn(data=request.data)
        s.is_valid(raise_exception=True)
        try:
            row = products.create(s.validated_data)
        except DB_ERRORS as exc:
            return db_error_response(exc)
        return Response(row, status=status.HTTP_201_CREATED)


class ProductDetailView(APIView):
    def get(self, request, pk):
        row = products.get(pk)
        if row is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(row, headers={"ETag": f'"{row["version"]}"'})

    def patch(self, request, pk):
        s = ProductPatch(data=request.data)
        s.is_valid(raise_exception=True)
        if_match = request.headers.get("If-Match")
        if if_match is not None and not if_match.strip('"').isdigit():
            return Response({"error": "If-Match"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            if if_match is None:
                row = products.update(pk, s.validated_data)
            else:
                row = inventory.update_if_version(pk, s.validated_data, int(if_match.strip('"')))
        except VersionConflict:
            return Response({"error": "version_conflict"}, status=status.HTTP_412_PRECONDITION_FAILED)
        except DB_ERRORS as exc:
            return db_error_response(exc)
        if row is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(row, headers={"ETag": f'"{row["version"]}"'})

    def delete(self, request, pk):
        if not products.delete(pk):
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductReserveView(APIView):
    """POST /api/products/<pk>/reserve/ {"qty": n} → 재고 차감. 부족하면 409."""

    def post(self, request, pk):
        try:
            qty = int(request.data.get("qty", 1))
        except (TypeError, ValueError):
            qty = 0
        if qty <= 0:
            return Response({"error": "qty"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            stock = inventory.reserve_atomic(pk, qty)
        except inventory.OutOfStock:
            return Response({"error": "out_of_stock"}, status=status.HTTP_409_CONFLICT)
        return Response({"stock": stock})


class OrderCreateView(APIView):
    """POST /api/orders/ + Idempotency-Key 헤더. 같은 키의 재요청은 같은 주문을 200으로 돌려준다."""

    def post(self, request):
        key = request.headers.get("Idempotency-Key")
        if not key:
            return Response({"error": "Idempotency-Key 헤더가 필요하다"}, status=status.HTTP_400_BAD_REQUEST)
        d = request.data
        try:
            customer_id, product_id, qty = (int(d[k]) for k in ("customer_id", "product_id", "qty"))
        except (KeyError, TypeError, ValueError):
            return Response({"error": "customer_id, product_id, qty(정수)가 필요하다"},
                            status=status.HTTP_400_BAD_REQUEST)
        if qty <= 0:
            return Response({"error": "qty"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order_id, created = external.create_order_idempotent(key, customer_id, product_id, qty)
        except inventory.OutOfStock:
            return Response({"error": "out_of_stock"}, status=status.HTTP_409_CONFLICT)
        except DB_ERRORS as exc:
            return db_error_response(exc)
        return Response({"id": order_id}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
