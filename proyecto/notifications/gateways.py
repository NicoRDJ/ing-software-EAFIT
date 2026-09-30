"""
Strangler Pattern (Taller 02): el envío de notificaciones se extrajo al
microservicio Flask (servicios/notificaciones). Cuando NOTIFICATIONS_SERVICE_URL
está configurado, el monolito deja de entregar mensajes por su cuenta y le
delega por HTTP al servicio v2; sin la variable (local, tests) se conserva el
comportamiento original in-process. Así la migración es reversible con solo
quitar una variable de entorno.
"""
import json
import logging
import urllib.error
import urllib.request

from django.conf import settings

from common.exceptions import UnsupportedNotificationChannelError
from notifications.factories import NotificationFactory
from notifications.notifiers import Notifier

logger = logging.getLogger("notifications")


class RemoteNotifier(Notifier):
    """Cumple el mismo contrato Notifier, pero la entrega ocurre en el microservicio."""

    def __init__(self, base_url: str, channel: str, timeout: float = 3.0):
        self._url = base_url.rstrip("/") + "/api/v2/notificaciones"
        self._channel = channel
        self._timeout = timeout

    def send(self, recipient: str, message: str) -> bool:
        payload = json.dumps({"channel": self._channel, "recipient": recipient, "message": message}).encode()
        req = urllib.request.Request(self._url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                return 200 <= resp.status < 300
        except (urllib.error.URLError, TimeoutError) as exc:
            # Fallo de entrega = dato que se registra (was_sent=False), no una excepción de negocio.
            logger.warning("Microservicio de notificaciones no disponible: %s", exc)
            return False


class RemoteNotifierFactory:
    """Misma interfaz que NotificationFactory: el Service Layer no nota la diferencia."""

    @classmethod
    def create(cls, channel: str) -> Notifier:
        if channel not in NotificationFactory._REGISTRY:
            raise UnsupportedNotificationChannelError(f"No notifier registered for channel '{channel}'.")
        return RemoteNotifier(settings.NOTIFICATIONS_SERVICE_URL, channel)


def default_notification_factory():
    return RemoteNotifierFactory if getattr(settings, "NOTIFICATIONS_SERVICE_URL", "") else NotificationFactory
