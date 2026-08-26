from rest_framework import serializers

from licensing.models import LicenseType
from sales.models import Coupon, Customer, DeliveryChannel, Order, OrderItem, Payment, PaymentMethod


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "full_name", "email", "customer_type", "country", "preferred_channel", "created_at"]
        read_only_fields = ["id", "created_at"]


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ["id", "code", "percentage_off", "valid_until", "is_active"]
        read_only_fields = ["id"]


class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    license_type = serializers.ChoiceField(choices=LicenseType.choices)
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    """Input contract for POST /api/orders/. Deliberately a plain Serializer,
    not a ModelSerializer — an order isn't created field-by-field on the
    Order model, it's created through OrderService.create_order(), so there
    is no single model this input maps onto 1:1."""

    customer_id = serializers.IntegerField()
    items = OrderItemInputSerializer(many=True, allow_empty=False)
    coupon_code = serializers.CharField(required=False, allow_blank=True, allow_null=True, default=None)
    delivery_channel = serializers.ChoiceField(choices=DeliveryChannel.choices, default=DeliveryChannel.EMAIL)
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class OrderItemOutputSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "license_type", "quantity", "unit_price", "subtotal"]


class OrderOutputSerializer(serializers.ModelSerializer):
    items = OrderItemOutputSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "customer", "coupon", "status", "delivery_channel",
            "notes", "total_amount", "items", "created_at",
        ]


class PaymentInputSerializer(serializers.Serializer):
    method = serializers.ChoiceField(choices=PaymentMethod.choices)
    transaction_reference = serializers.CharField(required=False, allow_blank=True, default="")


class PaymentOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "order", "amount", "method", "status", "transaction_reference", "processed_at"]
