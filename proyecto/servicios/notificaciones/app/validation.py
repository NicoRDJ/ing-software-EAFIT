"""Validación de la petición (sintaxis). La regla de negocio vive en routes/notifiers."""
import re

from .errors import ValidationError

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\+?[0-9]{7,15}$")
NOTIFICATION_TYPES = {"ORDER_CONFIRMATION", "KEY_DELIVERY", "ACTIVATION_HELP"}
MAX_MESSAGE = 1000


def parse_notification(payload) -> dict:
    if not isinstance(payload, dict):
        raise ValidationError("El cuerpo debe ser un objeto JSON.")

    errors: dict[str, str] = {}
    channel = str(payload.get("channel", "")).strip().upper()
    recipient = str(payload.get("recipient", "")).strip()
    message = str(payload.get("message", "")).strip()
    notification_type = str(payload.get("notification_type", "ORDER_CONFIRMATION")).strip().upper()
    order_id = payload.get("order_id")

    if not channel:
        errors["channel"] = "Campo obligatorio."
    if not recipient:
        errors["recipient"] = "Campo obligatorio."
    elif channel == "EMAIL" and not EMAIL_RE.match(recipient):
        errors["recipient"] = "Debe ser un correo válido para el canal EMAIL."
    elif channel in {"SMS", "WHATSAPP"} and not PHONE_RE.match(recipient.replace(" ", "")):
        errors["recipient"] = "Debe ser un teléfono válido (7-15 dígitos, opcional '+')."
    if not message:
        errors["message"] = "Campo obligatorio."
    elif len(message) > MAX_MESSAGE:
        errors["message"] = f"Máximo {MAX_MESSAGE} caracteres."
    if notification_type not in NOTIFICATION_TYPES:
        errors["notification_type"] = f"Use uno de: {', '.join(sorted(NOTIFICATION_TYPES))}."
    if order_id is not None and not isinstance(order_id, int):
        errors["order_id"] = "Debe ser un entero."

    if errors:
        raise ValidationError("La petición tiene campos inválidos.", errors)

    return {
        "channel": channel,
        "recipient": recipient,
        "message": message,
        "notification_type": notification_type,
        "order_id": order_id,
    }
