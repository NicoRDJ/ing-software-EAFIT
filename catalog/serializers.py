from rest_framework import serializers

from catalog.models import SoftwareProduct


class SoftwareProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoftwareProduct
        fields = ["id", "sku", "name", "category", "description", "base_price", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]
