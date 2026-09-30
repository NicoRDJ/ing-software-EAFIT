"""
Application service layer for the sales context.

Entregable 1 §2.2 is explicit: no business logic in views or serializers,
every principal business flow orchestrated by a class here, SRP evaluated
per class. Concretely that means each service below owns exactly one
use case:

- OrderService.create_order   -> the checkout flow (Builder -> persist -> allocate -> notify)
- OrderService.get_order/list -> read-only lookups, kept here so views never
                                  touch the ORM or translate DoesNotExist themselves
- LicenseAllocationService     -> "reserve enough AVAILABLE keys for this order,
                                  or fail loudly" — the one rule that can make
                                  checkout impossible even with valid input
- PaymentService                -> processing (simulated) a payment for an order
"""
from django.db import transaction
from django.utils import timezone

from catalog.models import SoftwareProduct
from common.exceptions import EntityNotFoundError, InsufficientLicenseStockError, PaymentConflictError
from licensing.models import LicenseKey, LicenseKeyStatus
from notifications.models import NotificationType
from notifications.services import NotificationService
from sales.builders import OrderBuilder
from sales.models import Coupon, Customer, Order, OrderItem, OrderStatus, Payment, PaymentStatus


class LicenseAllocationService:
    """Owns exactly one rule: an order can only be fulfilled if there are
    enough AVAILABLE license keys, of the right product + license type, to
    cover every item. Marks the keys SOLD and links them to their OrderItem
    as a side effect of a successful allocation."""

    def reserve_for_order(self, order: Order) -> None:
        for item in order.items.select_related("product"):
            available = list(
                LicenseKey.objects.select_for_update().filter(
                    product=item.product,
                    license_type=item.license_type,
                    status=LicenseKeyStatus.AVAILABLE,
                )[: item.quantity]
            )

            if len(available) < item.quantity:
                raise InsufficientLicenseStockError(
                    f"Only {len(available)} of {item.quantity} requested "
                    f"'{item.license_type}' keys available for {item.product.name}."
                )

            for key in available:
                key.status = LicenseKeyStatus.SOLD
                key.assigned_order_item = item
                key.save(update_fields=["status", "assigned_order_item"])


class OrderService:
    """Orchestrates the checkout use case end to end. Both collaborators are
    injectable (constructor defaults to the real implementations) so this
    service — and anything that depends on it — can be tested without a real
    notification send or without a real allocation strategy."""

    def __init__(
        self,
        notification_service: NotificationService | None = None,
        license_allocator: LicenseAllocationService | None = None,
    ):
        self._notifications = notification_service or NotificationService()
        self._license_allocator = license_allocator or LicenseAllocationService()

    @transaction.atomic
    def create_order(
        self,
        *,
        customer_id: int,
        items: list[dict],
        coupon_code: str | None,
        delivery_channel: str,
        notes: str = "",
    ) -> Order:
        customer = self._get_customer(customer_id)

        builder = (
            OrderBuilder()
            .for_customer(customer)
            .with_delivery_channel(delivery_channel)
            .with_notes(notes)
        )
        for item in items:
            product = self._get_product(item["product_id"])
            builder.add_item(product, item["license_type"], item["quantity"])

        coupon = self._get_coupon(coupon_code) if coupon_code else None
        builder.with_coupon(coupon)

        built = builder.build()

        order = Order.objects.create(
            customer=built.customer,
            coupon=built.coupon,
            delivery_channel=built.delivery_channel,
            notes=built.notes,
            total_amount=built.total_amount,
            status=OrderStatus.PENDING,
        )
        OrderItem.objects.bulk_create(
            [
                OrderItem(
                    order=order,
                    product=pending.product,
                    license_type=pending.license_type,
                    quantity=pending.quantity,
                    unit_price=pending.product.base_price,
                )
                for pending in built.items
            ]
        )

        self._license_allocator.reserve_for_order(order)

        self._notifications.notify(
            order=order,
            channel=order.delivery_channel,
            notification_type=NotificationType.ORDER_CONFIRMATION,
            recipient=customer.email,
            message=f"Order #{order.id} received — total {order.total_amount}.",
        )

        return order

    def get_order(self, order_id: int) -> Order:
        try:
            return Order.objects.prefetch_related("items").get(pk=order_id)
        except Order.DoesNotExist as exc:
            raise EntityNotFoundError(f"Order {order_id} not found.") from exc

    def list_orders_for_customer(self, customer_id: int):
        self._get_customer(customer_id)
        return Order.objects.filter(customer_id=customer_id).prefetch_related("items")

    def _get_customer(self, customer_id: int) -> Customer:
        try:
            return Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist as exc:
            raise EntityNotFoundError(f"Customer {customer_id} not found.") from exc

    def _get_product(self, product_id: int) -> SoftwareProduct:
        try:
            return SoftwareProduct.objects.get(pk=product_id, is_active=True)
        except SoftwareProduct.DoesNotExist as exc:
            raise EntityNotFoundError(f"Product {product_id} not found.") from exc

    def _get_coupon(self, code: str) -> Coupon:
        try:
            return Coupon.objects.get(code=code)
        except Coupon.DoesNotExist as exc:
            raise EntityNotFoundError(f"Coupon '{code}' not found.") from exc


class PaymentService:
    """Owns the payment-conflict rule: an order can be paid at most once, and
    only while it's still PENDING. In production, `_charge` is where a real
    gateway SDK call would go — swapping providers would mean changing this
    one method, not anything that calls PaymentService."""

    def process_payment(self, *, order: Order, method: str, transaction_reference: str = "") -> Payment:
        if hasattr(order, "payment"):
            raise PaymentConflictError(f"Order {order.id} already has a payment.")
        if order.status != OrderStatus.PENDING:
            raise PaymentConflictError(f"Order {order.id} is not payable in its current status ({order.status}).")

        reference = self._charge(order=order, method=method, transaction_reference=transaction_reference)

        payment = Payment.objects.create(
            order=order,
            amount=order.total_amount,
            method=method,
            status=PaymentStatus.COMPLETED,
            transaction_reference=reference,
        )
        from django.utils import timezone

        payment.processed_at = timezone.now()
        payment.save(update_fields=["processed_at"])

        order.status = OrderStatus.PAID

        order.save(update_fields=["status"])
        return payment

    def _charge(self, *, order: Order, method: str, transaction_reference: str) -> str:
        """Simulated gateway call — always succeeds. A real integration would
        raise PaymentConflictError (or a dedicated PaymentDeclinedError) on
        failure, which the existing exception handler would already know how
        to translate to an HTTP response without any view changes."""
        if transaction_reference:
            return transaction_reference

        return f"SIM-{order.id}-{int(timezone.now().timestamp())}"
