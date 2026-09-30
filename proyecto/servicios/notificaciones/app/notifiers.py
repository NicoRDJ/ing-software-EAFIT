"""Canales de entrega (Factory Method).

Misma idea que notifications/factories.py del monolito, ahora aislada en su
propio servicio: agregar un canal nuevo es registrar una clase, sin tocar la
ruta HTTP. Los envíos se simulan con un log porque no hay credenciales de
proveedores reales en el alcance del curso.
"""
import logging
from abc import ABC, abstractmethod

from .errors import UnsupportedChannelError

logger = logging.getLogger("notificaciones")


class Notifier(ABC):
    @abstractmethod
    def send(self, recipient: str, message: str) -> bool:
        """Entrega el mensaje; True si el proveedor lo aceptó."""


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


class NotifierFactory:
    _REGISTRY: dict[str, type[Notifier]] = {
        "EMAIL": EmailNotifier,
        "SMS": SMSNotifier,
        "WHATSAPP": WhatsAppNotifier,
    }

    @classmethod
    def channels(cls) -> list[str]:
        return list(cls._REGISTRY)

    @classmethod
    def create(cls, channel: str) -> Notifier:
        notifier_cls = cls._REGISTRY.get(channel)
        if notifier_cls is None:
            raise UnsupportedChannelError(
                f"El canal '{channel}' no está soportado.", {"channel": f"Use uno de: {', '.join(cls.channels())}"}
            )
        return notifier_cls()
