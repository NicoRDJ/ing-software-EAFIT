from django.test import TestCase

from licensing.models import LicenseType
from notifications.models import NotificationType
from notifications.notifiers import Notifier
from notifications.services import NotificationService
from sales.builders import OrderBuilder
from sales.models import Order, OrderItem, OrderStatus
from sales.tests.helpers import make_customer, make_product


class _RecordingNotifier(Notifier):
    """A fake used to prove NotificationService never has to hit a real
    provider to be tested — this is the concrete answer to the 'can I test
    the service without sending a real notification?' question in the
    project's architecture self-check (see DEFENSE_GUIDE.md)."""

    sent_messages: list[tuple[str, str]] = []

    def send(self, recipient: str, message: str) -> bool:
        self._class_sent().append((recipient, message))
        return True

    @classmethod
    def _class_sent(cls):
        return cls.sent_messages


class _FakeFactory:
    @classmethod
    def create(cls, channel: str) -> Notifier:
        return _RecordingNotifier()


class NotificationServiceTests(TestCase):
    def setUp(self):
        _RecordingNotifier.sent_messages = []
        customer = make_customer()
        product = make_product()
        built = OrderBuilder().for_customer(customer).add_item(product, LicenseType.RETAIL, 1).build()
        self.order = Order.objects.create(
            customer=built.customer, total_amount=built.total_amount, status=OrderStatus.PENDING
        )
        OrderItem.objects.create(
            order=self.order, product=product, license_type=LicenseType.RETAIL, quantity=1, unit_price=product.base_price
        )

    def test_notify_uses_injected_factory_instead_of_real_provider(self):
        service = NotificationService(factory=_FakeFactory)
        notification = service.notify(
            order=self.order,
            channel="EMAIL",
            notification_type=NotificationType.ORDER_CONFIRMATION,
            recipient="nico@test.com",
            message="hi",
        )
        self.assertTrue(notification.was_sent)
        self.assertEqual(_RecordingNotifier.sent_messages, [("nico@test.com", "hi")])
