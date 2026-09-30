from django.contrib import admin

from catalog.models import SoftwareProduct


@admin.register(SoftwareProduct)
class SoftwareProductAdmin(admin.ModelAdmin):
    list_display = ["sku", "name", "category", "base_price", "is_active"]
    list_filter = ["category", "is_active"]
    search_fields = ["sku", "name"]
