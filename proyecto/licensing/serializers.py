from rest_framework import serializers

from licensing.models import ActivationRecord, LicenseKey


class LicenseKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseKey
        fields = ["id", "product", "license_type", "key_code", "region", "activation_limit", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]


class ActivationInputSerializer(serializers.Serializer):
    device_fingerprint = serializers.CharField(max_length=128)


class ActivationOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivationRecord
        fields = ["id", "license_key", "device_fingerprint", "activated_at", "is_valid"]
