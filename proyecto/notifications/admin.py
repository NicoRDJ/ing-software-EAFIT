from django.contrib import admin

from notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["order", "channel", "notification_type", "recipient", "was_sent", "sent_at"]
    list_filter = ["channel", "notification_type", "was_sent"]
