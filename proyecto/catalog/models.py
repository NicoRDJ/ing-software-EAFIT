from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class ProductCategory(models.TextChoices):
    OPERATING_SYSTEM = "OS", "Operating System"
    OFFICE_SUITE = "OFFICE", "Office Suite"
    SERVER = "SERVER", "Server"
    SECURITY = "SECURITY", "Security"
    OTHER = "OTHER", "Other"


class SoftwareProduct(models.Model):
    """A sellable software product (e.g. 'Windows 11 Pro'), independent of any
    specific license key. LicenseKey instances (licensing app) are the actual
    sellable inventory for a given product + license type combination."""

    sku = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=16, choices=ProductCategory.choices)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.sku})"
