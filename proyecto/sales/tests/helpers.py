"""Shared object-creation helpers for tests across apps. Deliberately named
`helpers`, not `factories`, so it is never confused with the Factory design
pattern implemented in notifications/factories.py."""
from decimal import Decimal

from django.utils import timezone

from catalog.models import ProductCategory, SoftwareProduct
from licensing.models import LicenseKey, LicenseType
from sales.models import Coupon, Customer


def make_product(sku="WIN11PRO", name="Windows 11 Pro", price="120.00"):
    return SoftwareProduct.objects.create(
        sku=sku, name=name, category=ProductCategory.OPERATING_SYSTEM, base_price=Decimal(price)
    )


def make_customer(email="nico@test.com", full_name="Nico Test"):
    return Customer.objects.create(full_name=full_name, email=email)


def make_license_key(product, license_type=LicenseType.RETAIL, activation_limit=1, key_code=None):
    code = key_code or f"KEY-{product.sku}-{LicenseKey.objects.count()}"
    return LicenseKey.objects.create(
        product=product, license_type=license_type, key_code=code, activation_limit=activation_limit
    )


def make_coupon(code="SAVE10", percentage_off="10", days_valid=1, is_active=True):
    return Coupon.objects.create(
        code=code,
        percentage_off=Decimal(percentage_off),
        valid_until=timezone.now() + timezone.timedelta(days=days_valid),
        is_active=is_active,
    )
