"""입력 검증만 DRF Serializer에 맡긴다(ModelSerializer가 아니다)."""
from rest_framework import serializers


class ProductIn(serializers.Serializer):
    sku = serializers.CharField(max_length=64)
    name = serializers.CharField(max_length=200)
    category = serializers.CharField(max_length=50)
    price = serializers.IntegerField(min_value=0)
    stock = serializers.IntegerField(min_value=0)


class ProductPatch(serializers.Serializer):
    name = serializers.CharField(max_length=200, required=False)
    category = serializers.CharField(max_length=50, required=False)
    price = serializers.IntegerField(min_value=0, required=False)
    stock = serializers.IntegerField(min_value=0, required=False)

    def to_internal_value(self, data):
        # DRF는 모르는 필드를 조용히 버린다. 오타(stok)가 무시되지 않도록 막는다.
        unknown = set(data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError({f: "수정할 수 없는 필드다" for f in sorted(unknown)})
        if not data:
            raise serializers.ValidationError({"non_field_errors": ["수정할 필드가 없다"]})
        return super().to_internal_value(data)
