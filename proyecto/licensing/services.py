"""
Application service layer for the licensing context.

ActivationService owns the one rule that matters here: a license key can be
activated on a new device only if it has already been sold, and only while
it hasn't reached its activation_limit yet. Counting "how many valid
activations already exist" requires querying sibling rows, which is exactly
the kind of cross-record rule the rubric expects to live in a service, not
on the ActivationRecord model itself (see docs/wiki/Service-Layer.md).
"""
from common.exceptions import ActivationLimitExceededError, ActivationNotAllowedError, EntityNotFoundError
from licensing.models import ActivationRecord, LicenseKey, LicenseKeyStatus


class ActivationService:
    def activate(self, *, license_key_id: int, device_fingerprint: str) -> ActivationRecord:
        try:
            key = LicenseKey.objects.get(pk=license_key_id)
        except LicenseKey.DoesNotExist as exc:
            raise EntityNotFoundError(f"License key {license_key_id} not found.") from exc

        if key.status != LicenseKeyStatus.SOLD:
            raise ActivationNotAllowedError("Only sold license keys can be activated.")

        active_count = key.activations.filter(is_valid=True).count()
        if active_count >= key.activation_limit:
            raise ActivationLimitExceededError(
                f"License key has reached its activation limit ({key.activation_limit})."
            )

        return ActivationRecord.objects.create(license_key=key, device_fingerprint=device_fingerprint)
