from django.contrib import admin

from licensing.models import ActivationRecord, LicenseKey


@admin.register(LicenseKey)
class LicenseKeyAdmin(admin.ModelAdmin):
    list_display = ["key_code", "product", "license_type", "status", "activation_limit"]
    list_filter = ["license_type", "status"]
    search_fields = ["key_code"]


@admin.register(ActivationRecord)
class ActivationRecordAdmin(admin.ModelAdmin):
    list_display = ["license_key", "device_fingerprint", "activated_at", "is_valid"]
    list_filter = ["is_valid"]
