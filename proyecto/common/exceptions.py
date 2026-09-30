"""
Domain/application-level exceptions.

These are raised by services (never by views or serializers) whenever a
business rule is violated. They carry no knowledge of HTTP — the mapping to
status codes lives entirely in ``common/drf_exception_handler.py`` so the
presentation layer stays a translation boundary, not a rules engine.
"""


class DomainError(Exception):
    """Base class for every business-rule violation in the system."""

    default_message = "A domain error occurred."

    def __init__(self, message: str | None = None):
        super().__init__(message or self.default_message)


class EntityNotFoundError(DomainError):
    """Raised when a referenced entity (customer, product, order...) does not exist."""

    default_message = "Entity not found."


class InvalidOrderError(DomainError):
    """Raised when an order request violates a structural invariant (no items, no customer, invalid coupon)."""

    default_message = "Invalid order request."


class InsufficientLicenseStockError(DomainError):
    """Raised when there are not enough AVAILABLE license keys to satisfy an order item."""

    default_message = "Insufficient license key stock."


class PaymentConflictError(DomainError):
    """Raised when a payment is attempted against an order that cannot accept one right now."""

    default_message = "Payment conflict."


class ActivationNotAllowedError(DomainError):
    """Raised when activation is attempted on a license key that has not been sold."""

    default_message = "Activation not allowed for this license key."


class ActivationLimitExceededError(DomainError):
    """Raised when a license key has already reached its maximum number of valid activations."""

    default_message = "Activation limit exceeded."


class UnsupportedNotificationChannelError(DomainError):
    """Raised by the NotificationFactory when asked to build a notifier for an unknown channel."""

    default_message = "Unsupported notification channel."
