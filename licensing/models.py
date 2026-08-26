from django.db import models

from catalog.models import SoftwareProduct


class LicenseType(models.TextChoices):
    RETAIL = "RETAIL", "Retail"
    OEM = "OEM", "OEM"
    MAK = "MAK", "MAK (Multiple Activation Key)"
    VOLUME = "VOLUME", "Volume License"


class LicenseKeyStatus(models.TextChoices):
    AVAILABLE = "AVAILABLE", "Available"
    SOLD = "SOLD", "Sold"
    REVOKED = "REVOKED", "Revoked"


class LicenseKey(models.Model):
    """A single, real, sellable license key. This is inventory, not a product
    definition — many LicenseKey rows can point at the same SoftwareProduct.

    The FK to sales.OrderItem is declared as a lazy string reference
    ("sales.OrderItem") rather than an import, so the licensing app never has
    to import sales.models at module load time — sales.models does import
    licensing.models (for the LicenseType choices), and a real circular
    import would break Django's app loading. See docs/wiki/Architecture.md.
    """

    product = models.ForeignKey(SoftwareProduct, related_name="license_keys", on_delete=models.CASCADE)
    license_type = models.CharField(max_length=16, choices=LicenseType.choices)
    key_code = models.CharField(max_length=64, unique=True)
    region = models.CharField(max_length=32, default="GLOBAL")
    activation_limit = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(max_length=16, choices=LicenseKeyStatus.choices, default=LicenseKeyStatus.AVAILABLE)
    assigned_order_item = models.ForeignKey(
        "sales.OrderItem",
        related_name="assigned_keys",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["product", "license_type", "status"])]

    def __str__(self) -> str:
        return f"{self.product.sku} · {self.license_type} · {self.status}"


class ActivationRecord(models.Model):
    """One activation attempt of a LicenseKey on a device. Whether a new
    activation is *allowed* (activation_limit not yet reached) is a
    cross-record business rule enforced by ActivationService, not here —
    a single ActivationRecord has no way to know about its siblings without
    querying the database, which is a service/repository concern."""

    license_key = models.ForeignKey(LicenseKey, related_name="activations", on_delete=models.CASCADE)
    device_fingerprint = models.CharField(max_length=128)
    activated_at = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)

    class Meta:
        ordering = ["-activated_at"]

    def __str__(self) -> str:
        return f"{self.license_key.key_code} -> {self.device_fingerprint[:12]}"
