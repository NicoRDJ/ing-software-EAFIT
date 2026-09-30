from django.contrib import admin

from sales.models import Coupon, Customer, Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["subtotal"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "customer", "status", "total_amount", "created_at"]
    list_filter = ["status", "delivery_channel"]
    inlines = [OrderItemInline]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email", "customer_type", "country"]
    search_fields = ["full_name", "email"]


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ["code", "percentage_off", "valid_until", "is_active"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["order", "amount", "method", "status", "processed_at"]
