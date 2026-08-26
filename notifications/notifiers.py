"""
Notifier implementations.

Each Notifier knows how to deliver a message over exactly one channel. None
of them know *why* a message is being sent (that's NotificationService's
job) or *which* one to use for a given order (that's NotificationFactory's
job) — this file is the "variant behavior" side of the Factory pattern, not
the selection logic.

Real provider SDKs (SES, Twilio, WhatsApp Business API...) would be wired in
here behind the same `send()` contract; for this deliverable the send is
simulated and logged, since no external credentials are in scope.
"""
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger("notifications")


class Notifier(ABC):
    """Common contract every channel implementation must satisfy. Depending on
    this abstraction (rather than a concrete EmailNotifier) is what lets
    NotificationService stay ignorant of *how* a message actually travels —
    the Dependency Inversion half of the Factory pattern's payoff."""

    @abstractmethod
    def send(self, recipient: str, message: str) -> bool:
        """Attempt delivery; return True on success, False on failure. Never
        raises for an ordinary delivery failure — that's a fact the caller
        records (Notification.was_sent), not an exceptional condition."""
        raise NotImplementedError


class EmailNotifier(Notifier):
    def send(self, recipient: str, message: str) -> bool:
        logger.info("EMAIL -> %s: %s", recipient, message)
        return True


class SMSNotifier(Notifier):
    def send(self, recipient: str, message: str) -> bool:
        logger.info("SMS -> %s: %s", recipient, message)
        return True


class WhatsAppNotifier(Notifier):
    def send(self, recipient: str, message: str) -> bool:
        logger.info("WHATSAPP -> %s: %s", recipient, message)
        return True
