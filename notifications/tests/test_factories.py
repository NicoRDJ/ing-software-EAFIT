from django.test import TestCase

from common.exceptions import UnsupportedNotificationChannelError
from notifications.factories import NotificationFactory
from notifications.models import NotificationChannel
from notifications.notifiers import EmailNotifier, SMSNotifier, WhatsAppNotifier


class NotificationFactoryTests(TestCase):
    def test_creates_email_notifier_for_email_channel(self):
        self.assertIsInstance(NotificationFactory.create(NotificationChannel.EMAIL), EmailNotifier)

    def test_creates_sms_notifier_for_sms_channel(self):
        self.assertIsInstance(NotificationFactory.create(NotificationChannel.SMS), SMSNotifier)

    def test_creates_whatsapp_notifier_for_whatsapp_channel(self):
        self.assertIsInstance(NotificationFactory.create(NotificationChannel.WHATSAPP), WhatsAppNotifier)

    def test_unknown_channel_raises_unsupported_channel_error(self):
        with self.assertRaises(UnsupportedNotificationChannelError):
            NotificationFactory.create("CARRIER_PIGEON")

    def test_notifier_send_contract_returns_bool(self):
        notifier = NotificationFactory.create(NotificationChannel.EMAIL)
        result = notifier.send("nico@test.com", "hello")
        self.assertIsInstance(result, bool)
