"""
Populates a small, realistic demo dataset so the checkout -> payment ->
activation flow can be exercised immediately from a fresh database — used
for the defense/sustentación demo (see README.md "How to Demo It").

This is intentionally a management command, not an API endpoint or a
migration: it's operator tooling, not part of the domain's public contract.
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from catalog.models import ProductCategory, SoftwareProduct
from licensing.models import LicenseKey, LicenseType
from sales.models import Coupon, Customer


class Command(BaseCommand):
    help = "Seed a demo product, license keys, a customer and a coupon for manual/API testing."

    def handle(self, *args, **options):
        product, created = SoftwareProduct.objects.get_or_create(
            sku="WIN11PRO",
            defaults=dict(
                name="Windows 11 Pro",
                category=ProductCategory.OPERATING_SYSTEM,
                description="Retail/OEM/MAK keys for Windows 11 Pro.",
                base_price=Decimal("120.00"),
            ),
        )
        self.stdout.write(self._status("SoftwareProduct", product.sku, created))

        office, created = SoftwareProduct.objects.get_or_create(
            sku="OFFICE2024",
            defaults=dict(
                name="Microsoft Office 2024 Home & Business",
                category=ProductCategory.OFFICE_SUITE,
                description="One-time-purchase Office 2024 license.",
                base_price=Decimal("149.00"),
            ),
        )
        self.stdout.write(self._status("SoftwareProduct", office.sku, created))

        for i in range(3):
            key, created = LicenseKey.objects.get_or_create(
                key_code=f"WIN11-RETAIL-DEMO-{i}",
                defaults=dict(product=product, license_type=LicenseType.RETAIL, activation_limit=1),
            )
            self.stdout.write(self._status("LicenseKey", key.key_code, created))

        for i in range(2):
            key, created = LicenseKey.objects.get_or_create(
                key_code=f"OFFICE-OEM-DEMO-{i}",
                defaults=dict(product=office, license_type=LicenseType.OEM, activation_limit=1),
            )
            self.stdout.write(self._status("LicenseKey", key.key_code, created))

        customer, created = Customer.objects.get_or_create(
            email="demo.customer@mylegitkeys.test",
            defaults=dict(full_name="Demo Customer"),
        )
        self.stdout.write(self._status("Customer", customer.email, created))

        coupon, created = Coupon.objects.get_or_create(
            code="EAFIT10",
            defaults=dict(percentage_off=Decimal("10"), valid_until=timezone.now() + timezone.timedelta(days=30)),
        )
        self.stdout.write(self._status("Coupon", coupon.code, created))

        self.stdout.write(self.style.SUCCESS("\nDemo data ready. Sample IDs:"))
        self.stdout.write(f"  product.id (Windows 11 Pro) = {product.id}")
        self.stdout.write(f"  product.id (Office 2024)    = {office.id}")
        self.stdout.write(f"  customer.id                 = {customer.id}")
        self.stdout.write(f"  coupon.code                 = {coupon.code}")

    def _status(self, label: str, key: str, created: bool) -> str:
        verb = "created" if created else "already existed"
        return f"  {label} '{key}' {verb}"
