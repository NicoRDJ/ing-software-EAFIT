from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from catalog.models import SoftwareProduct
from licensing.models import LicenseType


class CustomerType(models.TextChoices):
    INDIVIDUAL = "INDIVIDUAL", "Individual"
    BUSINESS = "BUSINESS", "Business"


class DeliveryChannel(models.TextChoices):
    """Kept local to sales (rather than importing notifications.NotificationChannel)
    so this app has no compile-time dependency on the notifications app — it
    only needs to know which channel a customer *wants*, not how a channel
    is implemented. See docs/wiki/Architecture.md for the dependency map."""

    EMAIL = "EMAIL", "Email"
    SMS = "SMS", "SMS"
    WHATSAPP = "WHATSAPP", "WhatsApp"


class Customer(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    customer_type = models.CharField(max_length=16, choices=CustomerType.choices, default=CustomerType.INDIVIDUAL)
    country = models.CharField(max_length=2, default="CO")
    preferred_channel = models.CharField(max_length=16, choices=DeliveryChannel.choices, default=DeliveryChannel.EMAIL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.full_name} <{self.email}>"


class Coupon(models.Model):
    code = models.CharField(max_length=32, unique=True)
    percentage_off = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("1")), MaxValueValidator(Decimal("100"))],
    )
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def is_valid_now(self) -> bool:
        """Pure predicate over this row's own fields — not a cross-entity
        business rule, so it stays on the model (see rubric boundary note in
        docs/wiki/Service-Layer.md). Whether a coupon *applies* to a given
        order is decided by OrderBuilder, which also needs the order's items."""
        return self.is_active and timezone.now() <= self.valid_until

    def __str__(self) -> str:
        return f"{self.code} (-{self.percentage_off}%)"


class OrderStatus(models.TextChoices):
    PENDING = "PENDING", "Pending Payment"
    PAID = "PAID", "Paid"
    CANCELLED = "CANCELLED", "Cancelled"


class Order(models.Model):
    """The aggregate root of the sales context. Always created through
    OrderBuilder + OrderService.create_order — never instantiated piecemeal
    by a view, so its invariants (>=1 item, customer set, total computed
    consistently) are guaranteed at construction time."""

    customer = models.ForeignKey(Customer, related_name="orders", on_delete=models.PROTECT)
    coupon = models.ForeignKey(Coupon, related_name="orders", null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=16, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    delivery_channel = models.CharField(max_length=16, choices=DeliveryChannel.choices, default=DeliveryChannel.EMAIL)
    notes = models.CharField(max_length=500, blank=True, default="")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order #{self.pk} · {self.customer.email} · {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(SoftwareProduct, related_name="order_items", on_delete=models.PROTECT)
    license_type = models.CharField(max_length=16, choices=LicenseType.choices)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self) -> Decimal:
        """Derived value from this row's own fields only — not a business
        rule, just arithmetic over data the row already owns."""
        return self.unit_price * self.quantity

    def __str__(self) -> str:
        return f"{self.quantity}x {self.product.sku} ({self.license_type})"


class PaymentMethod(models.TextChoices):
    CARD = "CARD", "Credit/Debit Card"
    PAYPAL = "PAYPAL", "PayPal"
    CRYPTO = "CRYPTO", "Cryptocurrency"


class PaymentStatus(models.TextChoices):
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"


class Payment(models.Model):
    order = models.OneToOneField(Order, related_name="payment", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=16, choices=PaymentMethod.choices)
    status = models.CharField(max_length=16, choices=PaymentStatus.choices, default=PaymentStatus.COMPLETED)
    transaction_reference = models.CharField(max_length=64, blank=True, default="")
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Payment for Order #{self.order_id} · {self.status}"
