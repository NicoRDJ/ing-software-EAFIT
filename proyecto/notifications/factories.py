"""
Factory pattern — required by Entregable 1 §2.4 to manage "a dependency
external or variant of logic" (the brief's own examples: notifications,
payment gateways, report generators). Notifications is the natural fit here:
which channel a customer receives their license key on (Email / SMS /
WhatsApp) is exactly the kind of decision that should not leak into
OrderService as a chain of if/elif statements.

Why this matters concretely for this business: the operational audit this
project is based on (MyLegitKeys) surfaced a real customer complaint about
being unreachable over both email and WhatsApp after a support issue — i.e.
channel diversity and channel *reliability* is a genuine pain point for this
kind of business, not an academic exercise. Making the channel a pluggable
dependency is what would let a future entrega add a "retry on a different
channel if the first one fails" policy without touching OrderService at all.
"""
from common.exceptions import UnsupportedNotificationChannelError
from notifications.models import NotificationChannel
from notifications.notifiers import EmailNotifier, Notifier, SMSNotifier, WhatsAppNotifier


class NotificationFactory:
    _REGISTRY: dict[str, type[Notifier]] = {
        NotificationChannel.EMAIL: EmailNotifier,
        NotificationChannel.SMS: SMSNotifier,
        NotificationChannel.WHATSAPP: WhatsAppNotifier,
    }

    @classmethod
    def create(cls, channel: str) -> Notifier:
        notifier_cls = cls._REGISTRY.get(channel)
        if notifier_cls is None:
            raise UnsupportedNotificationChannelError(f"No notifier registered for channel '{channel}'.")
        return notifier_cls()
