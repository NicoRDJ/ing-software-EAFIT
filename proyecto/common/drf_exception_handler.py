"""
Central translation point from domain exceptions to HTTP responses.

Views never catch DomainError subclasses themselves — they let them
propagate, and DRF routes every unhandled exception raised inside a view
through settings.REST_FRAMEWORK['EXCEPTION_HANDLER']. This keeps the
"which HTTP status does rule X map to" decision in exactly one place
instead of scattered across every view's try/except blocks.
"""
from rest_framework import status as http_status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_default_handler

from common.exceptions import (
    ActivationLimitExceededError,
    ActivationNotAllowedError,
    DomainError,
    EntityNotFoundError,
    InsufficientLicenseStockError,
    InvalidOrderError,
    PaymentConflictError,
    UnsupportedNotificationChannelError,
)

_STATUS_BY_EXCEPTION = {
    EntityNotFoundError: http_status.HTTP_404_NOT_FOUND,
    InvalidOrderError: http_status.HTTP_400_BAD_REQUEST,
    UnsupportedNotificationChannelError: http_status.HTTP_400_BAD_REQUEST,
    InsufficientLicenseStockError: http_status.HTTP_409_CONFLICT,
    PaymentConflictError: http_status.HTTP_409_CONFLICT,
    ActivationNotAllowedError: http_status.HTTP_409_CONFLICT,
    ActivationLimitExceededError: http_status.HTTP_409_CONFLICT,
}


def domain_exception_handler(exc, context):
    """Map DomainError subclasses to HTTP responses; delegate everything else to DRF's default handler."""
    if isinstance(exc, DomainError):
        status_code = _STATUS_BY_EXCEPTION.get(type(exc), http_status.HTTP_400_BAD_REQUEST)
        message = exc.args[0] if exc.args else str(exc)
        return Response({"error": message}, status=status_code)

    return drf_default_handler(exc, context)
