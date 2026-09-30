from rest_framework import status
from rest_framework.test import APITestCase

from licensing.models import LicenseKeyStatus
from sales.tests.helpers import make_license_key, make_product


class LicenseKeyActivationApiTests(APITestCase):
    def setUp(self):
        self.product = make_product()
        self.key = make_license_key(self.product, activation_limit=1)
        self.key.status = LicenseKeyStatus.SOLD
        self.key.save(update_fields=["status"])

    def test_activation_returns_200(self):
        response = self.client.post(
            f"/api/license-keys/{self.key.id}/activate/", {"device_fingerprint": "DEV-1"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["device_fingerprint"], "DEV-1")

    def test_activation_missing_fingerprint_returns_400(self):
        response = self.client.post(f"/api/license-keys/{self.key.id}/activate/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_activation_on_unknown_key_returns_404(self):
        response = self.client.post(
            "/api/license-keys/999999/activate/", {"device_fingerprint": "DEV-1"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_activation_beyond_limit_returns_409(self):
        self.client.post(f"/api/license-keys/{self.key.id}/activate/", {"device_fingerprint": "DEV-1"}, format="json")
        response = self.client.post(
            f"/api/license-keys/{self.key.id}/activate/", {"device_fingerprint": "DEV-2"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_create_license_key_returns_201(self):
        response = self.client.post(
            "/api/license-keys/",
            {"product": self.product.id, "license_type": "RETAIL", "key_code": "NEW-KEY-1", "activation_limit": 1},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
