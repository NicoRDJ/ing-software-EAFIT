from django.utils import timezone

from notifications.factories import NotificationFactory
from notifications.gateways import default_notification_factory
from notifications.models import Notification


class NotificationService:
    """The only thing in the codebase allowed to talk to NotificationFactory.
    Takes the factory as a constructor parameter (defaulting to the real one)
    so tests — and OrderService's own tests — can inject a fake factory and
    assert on delivery without ever hitting a real send() implementation."""

    def __init__(self, factory: type[NotificationFactory] | None = None):
        # Sin factory explícita: in-process en local, microservicio v2 si NOTIFICATIONS_SERVICE_URL existe.
        self._factory = factory or default_notification_factory()

    def notify(self, *, order, channel: str, notification_type: str, recipient: str, message: str) -> Notification:
        notifier = self._factory.create(channel)
        was_sent = notifier.send(recipient, message)

        return Notification.objects.create(
            order=order,
            channel=channel,
            notification_type=notification_type,
            recipient=recipient,
            message=message,
            was_sent=was_sent,
            sent_at=timezone.now() if was_sent else None,
        )
