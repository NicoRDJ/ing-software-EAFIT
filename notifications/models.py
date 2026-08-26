from django.db import models

from sales.models import Order


class NotificationChannel(models.TextChoices):
    EMAIL = "EMAIL", "Email"
    SMS = "SMS", "SMS"
    WHATSAPP = "WHATSAPP", "WhatsApp"


class NotificationType(models.TextChoices):
    ORDER_CONFIRMATION = "ORDER_CONFIRMATION", "Order Confirmation"
    KEY_DELIVERY = "KEY_DELIVERY", "License Key Delivery"
    ACTIVATION_HELP = "ACTIVATION_HELP", "Activation Assistance"


class Notification(models.Model):
    """A record of a message that was (attempted to be) sent to a customer.
    Created exclusively by NotificationService, which is the only thing that
    knows how to pick and invoke a Notifier — see notifications/factories.py."""

    order = models.ForeignKey(Order, related_name="notifications", on_delete=models.CASCADE)
    channel = models.CharField(max_length=16, choices=NotificationChannel.choices)
    notification_type = models.CharField(max_length=32, choices=NotificationType.choices)
    recipient = models.CharField(max_length=255)
    message = models.TextField()
    was_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.notification_type} -> {self.recipient} via {self.channel}"
