from rest_framework import status
from rest_framework.test import APITestCase

from licensing.models import LicenseType
from sales.tests.helpers import make_customer, make_license_key, make_product


class OrderApiTests(APITestCase):
    def setUp(self):
        self.customer = make_customer()
        self.product = make_product(price="100.00")
        make_license_key(self.product)
        make_license_key(self.product)

    def _valid_payload(self, quantity=1):
        return {
            "customer_id": self.customer.id,
            "items": [{"product_id": self.product.id, "license_type": LicenseType.RETAIL, "quantity": quantity}],
            "delivery_channel": "EMAIL",
        }

    def test_create_order_returns_201(self):
        response = self.client.post("/api/orders/", self._valid_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "PENDING")
        self.assertEqual(len(response.data["items"]), 1)

    def test_create_order_with_empty_items_returns_400(self):
        payload = self._valid_payload()
        payload["items"] = []
        response = self.client.post("/api/orders/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_with_unknown_product_returns_404(self):
        payload = self._valid_payload()
        payload["items"][0]["product_id"] = 999999
        response = self.client.post("/api/orders/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_order_with_insufficient_stock_returns_409(self):
        response = self.client.post("/api/orders/", self._valid_payload(quantity=99), format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_get_unknown_order_returns_404(self):
        response = self.client.get("/api/orders/999999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_existing_order_returns_200(self):
        create_response = self.client.post("/api/orders/", self._valid_payload(), format="json")
        order_id = create_response.data["id"]

        response = self.client.get(f"/api/orders/{order_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], order_id)

    def test_payment_flow_second_attempt_returns_409(self):
        create_response = self.client.post("/api/orders/", self._valid_payload(), format="json")
        order_id = create_response.data["id"]

        first_payment = self.client.post(f"/api/orders/{order_id}/pay/", {"method": "CARD"}, format="json")
        self.assertEqual(first_payment.status_code, status.HTTP_200_OK)
        self.assertEqual(first_payment.data["status"], "COMPLETED")

        second_payment = self.client.post(f"/api/orders/{order_id}/pay/", {"method": "CARD"}, format="json")
        self.assertEqual(second_payment.status_code, status.HTTP_409_CONFLICT)

    def test_payment_for_unknown_order_returns_404(self):
        response = self.client.post("/api/orders/999999/pay/", {"method": "CARD"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CustomerApiTests(APITestCase):
    def test_create_customer_returns_201(self):
        response = self.client.post(
            "/api/customers/", {"full_name": "Ada Lovelace", "email": "ada@test.com"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_customer_with_duplicate_email_returns_400(self):
        make_customer(email="dup@test.com")
        response = self.client.post(
            "/api/customers/", {"full_name": "Someone Else", "email": "dup@test.com"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_orders_for_unknown_customer_returns_404(self):
        response = self.client.get("/api/customers/999999/orders/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
