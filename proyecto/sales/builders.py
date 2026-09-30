"""
Builder pattern — required by Entregable 1 §2.4 for "the most complex entity
in the system". That entity is Order: it has a required customer, a variable
number of line items (each with its own product/license type/quantity), an
optional coupon that must be validated before it can affect the total, an
optional delivery channel, and a total that has to be computed consistently
from all of the above *before* anything is allowed to hit the database.

OrderBuilder builds an in-memory, fully-validated `_BuiltOrder` — it never
touches the ORM. Persisting that result is OrderService's job (sales/services.py).
Keeping construction and persistence separate is what lets the builder's
invariants (>=1 item, valid coupon, positive quantities) be unit-tested with
zero database access.
"""
from dataclasses import dataclass, field
from decimal import Decimal

from common.exceptions import InvalidOrderError
from sales.models import Coupon, Customer, DeliveryChannel


@dataclass(frozen=True)
class _PendingItem:
    product: object
    license_type: str
    quantity: int


@dataclass(frozen=True)
class BuiltOrder:
    """Immutable result of a successful build() — everything OrderService
    needs to persist an Order + its OrderItems, already validated."""

    customer: Customer
    items: list = field(default_factory=list)
    coupon: Coupon | None = None
    delivery_channel: str = DeliveryChannel.EMAIL
    notes: str = ""
    total_amount: Decimal = Decimal("0")


class OrderBuilder:
    def __init__(self):
        self._customer: Customer | None = None
        self._items: list[_PendingItem] = []
        self._coupon: Coupon | None = None
        self._delivery_channel: str = DeliveryChannel.EMAIL
        self._notes: str = ""

    def for_customer(self, customer: Customer) -> "OrderBuilder":
        self._customer = customer
        return self

    def add_item(self, product, license_type: str, quantity: int) -> "OrderBuilder":
        if quantity <= 0:
            raise InvalidOrderError("Item quantity must be a positive integer.")
        self._items.append(_PendingItem(product=product, license_type=license_type, quantity=quantity))
        return self

    def with_coupon(self, coupon: Coupon | None) -> "OrderBuilder":
        if coupon is not None and not coupon.is_valid_now():
            raise InvalidOrderError(f"Coupon '{coupon.code}' is expired or inactive.")
        self._coupon = coupon
        return self

    def with_delivery_channel(self, channel: str) -> "OrderBuilder":
        self._delivery_channel = channel
        return self

    def with_notes(self, notes: str) -> "OrderBuilder":
        self._notes = notes
        return self

    def build(self) -> BuiltOrder:
        if self._customer is None:
            raise InvalidOrderError("An order requires a customer.")
        if not self._items:
            raise InvalidOrderError("An order requires at least one item.")

        subtotal = sum((item.product.base_price * item.quantity for item in self._items), Decimal("0"))
        discount = (subtotal * self._coupon.percentage_off / Decimal("100")) if self._coupon else Decimal("0")
        total = subtotal - discount

        return BuiltOrder(
            customer=self._customer,
            items=list(self._items),
            coupon=self._coupon,
            delivery_channel=self._delivery_channel,
            notes=self._notes,
            total_amount=total,
        )
