from decimal import Decimal

from django.test import TestCase

from common.exceptions import EntityNotFoundError, InsufficientLicenseStockError, PaymentConflictError
from licensing.models import LicenseKeyStatus, LicenseType
from sales.models import OrderStatus
from sales.services import OrderService, PaymentService
from sales.tests.helpers import make_customer, make_license_key, make_product


class OrderServiceCreateOrderTests(TestCase):
    def setUp(self):
        self.customer = make_customer()
        self.product = make_product(price="100.00")
        self.key_a = make_license_key(self.product)
        self.key_b = make_license_key(self.product)

    def test_create_order_happy_path_allocates_keys_and_notifies(self):
        order = OrderService().create_order(
            customer_id=self.customer.id,
            items=[{"product_id": self.product.id, "license_type": LicenseType.RETAIL, "quantity": 2}],
            coupon_code=None,
            delivery_channel="EMAIL",
        )
        self.assertEqual(order.status, OrderStatus.PENDING)
        self.assertEqual(order.total_amount, Decimal("200.00"))
        self.assertEqual(order.items.count(), 1)

        self.key_a.refresh_from_db()
        self.key_b.refresh_from_db()
        self.assertEqual(self.key_a.status, LicenseKeyStatus.SOLD)
        self.assertEqual(self.key_b.status, LicenseKeyStatus.SOLD)
        self.assertEqual(order.notifications.count(), 1)

    def test_create_order_with_unknown_customer_raises_not_found(self):
        with self.assertRaises(EntityNotFoundError):
            OrderService().create_order(
                customer_id=999999,
                items=[{"product_id": self.product.id, "license_type": LicenseType.RETAIL, "quantity": 1}],
                coupon_code=None,
                delivery_channel="EMAIL",
            )

    def test_create_order_with_unknown_product_raises_not_found(self):
        with self.assertRaises(EntityNotFoundError):
            OrderService().create_order(
                customer_id=self.customer.id,
                items=[{"product_id": 999999, "license_type": LicenseType.RETAIL, "quantity": 1}],
                coupon_code=None,
                delivery_channel="EMAIL",
            )

    def test_create_order_with_insufficient_stock_raises_and_rolls_back(self):
        with self.assertRaises(InsufficientLicenseStockError):
            OrderService().create_order(
                customer_id=self.customer.id,
                items=[{"product_id": self.product.id, "license_type": LicenseType.RETAIL, "quantity": 5}],
                coupon_code=None,
                delivery_channel="EMAIL",
            )
        # @transaction.atomic must have rolled back the partially-created Order.
        self.assertEqual(self.customer.orders.count(), 0)
        self.key_a.refresh_from_db()
        self.assertEqual(self.key_a.status, LicenseKeyStatus.AVAILABLE)


class PaymentServiceTests(TestCase):
    def setUp(self):
        self.customer = make_customer()
        self.product = make_product(price="50.00")
        make_license_key(self.product)
        self.order = OrderService().create_order(
            customer_id=self.customer.id,
            items=[{"product_id": self.product.id, "license_type": LicenseType.RETAIL, "quantity": 1}],
            coupon_code=None,
            delivery_channel="EMAIL",
        )

    def test_process_payment_marks_order_paid(self):
        payment = PaymentService().process_payment(order=self.order, method="CARD")
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, OrderStatus.PAID)
        self.assertEqual(payment.amount, self.order.total_amount)

    def test_second_payment_on_same_order_raises_conflict(self):
        PaymentService().process_payment(order=self.order, method="CARD")
        with self.assertRaises(PaymentConflictError):
            PaymentService().process_payment(order=self.order, method="CARD")
