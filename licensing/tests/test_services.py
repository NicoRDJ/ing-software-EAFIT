from django.test import TestCase

from common.exceptions import ActivationLimitExceededError, ActivationNotAllowedError, EntityNotFoundError
from licensing.models import LicenseKeyStatus
from licensing.services import ActivationService
from sales.tests.helpers import make_license_key, make_product


class ActivationServiceTests(TestCase):
    def setUp(self):
        self.product = make_product()
        self.key = make_license_key(self.product, activation_limit=2)

    def test_activation_on_unknown_key_raises_not_found(self):
        with self.assertRaises(EntityNotFoundError):
            ActivationService().activate(license_key_id=999999, device_fingerprint="DEV-1")

    def test_activation_on_key_not_yet_sold_is_not_allowed(self):
        self.assertEqual(self.key.status, LicenseKeyStatus.AVAILABLE)
        with self.assertRaises(ActivationNotAllowedError):
            ActivationService().activate(license_key_id=self.key.id, device_fingerprint="DEV-1")

    def test_activation_succeeds_within_limit(self):
        self.key.status = LicenseKeyStatus.SOLD
        self.key.save(update_fields=["status"])

        first = ActivationService().activate(license_key_id=self.key.id, device_fingerprint="DEV-1")
        second = ActivationService().activate(license_key_id=self.key.id, device_fingerprint="DEV-2")

        self.assertEqual(self.key.activations.count(), 2)
        self.assertNotEqual(first.device_fingerprint, second.device_fingerprint)

    def test_activation_beyond_limit_raises(self):
        self.key.status = LicenseKeyStatus.SOLD
        self.key.save(update_fields=["status"])
        ActivationService().activate(license_key_id=self.key.id, device_fingerprint="DEV-1")
        ActivationService().activate(license_key_id=self.key.id, device_fingerprint="DEV-2")

        with self.assertRaises(ActivationLimitExceededError):
            ActivationService().activate(license_key_id=self.key.id, device_fingerprint="DEV-3")
