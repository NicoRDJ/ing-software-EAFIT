from decimal import Decimal

from django.test import TestCase

from common.exceptions import InvalidOrderError
from licensing.models import LicenseType
from sales.builders import OrderBuilder
from sales.tests.helpers import make_coupon, make_customer, make_product


class OrderBuilderTests(TestCase):
    def setUp(self):
        self.customer = make_customer()
        self.product = make_product(price="100.00")

    def test_build_without_customer_raises(self):
        with self.assertRaises(InvalidOrderError):
            OrderBuilder().add_item(self.product, LicenseType.RETAIL, 1).build()

    def test_build_without_items_raises(self):
        with self.assertRaises(InvalidOrderError):
            OrderBuilder().for_customer(self.customer).build()

    def test_add_item_with_non_positive_quantity_raises(self):
        with self.assertRaises(InvalidOrderError):
            OrderBuilder().add_item(self.product, LicenseType.RETAIL, 0)

    def test_build_computes_total_without_coupon(self):
        built = (
            OrderBuilder()
            .for_customer(self.customer)
            .add_item(self.product, LicenseType.RETAIL, 2)
            .build()
        )
        self.assertEqual(built.total_amount, Decimal("200.00"))
        self.assertEqual(len(built.items), 1)

    def test_build_applies_valid_coupon_discount(self):
        coupon = make_coupon(percentage_off="10")
        built = (
            OrderBuilder()
            .for_customer(self.customer)
            .add_item(self.product, LicenseType.RETAIL, 2)
            .with_coupon(coupon)
            .build()
        )
        # 200.00 - 10% = 180.00
        self.assertEqual(built.total_amount, Decimal("180.000"))

    def test_expired_coupon_is_rejected(self):
        expired = make_coupon(code="EXPIRED", days_valid=-1)
        with self.assertRaises(InvalidOrderError):
            OrderBuilder().for_customer(self.customer).with_coupon(expired)

    def test_inactive_coupon_is_rejected(self):
        inactive = make_coupon(code="INACTIVE", is_active=False)
        with self.assertRaises(InvalidOrderError):
            OrderBuilder().for_customer(self.customer).with_coupon(inactive)

    def test_builder_is_chainable_and_reusable_per_instance(self):
        builder = OrderBuilder().for_customer(self.customer)
        builder.add_item(self.product, LicenseType.RETAIL, 1)
        builder.add_item(self.product, LicenseType.OEM, 3)
        built = builder.build()
        self.assertEqual(len(built.items), 2)
