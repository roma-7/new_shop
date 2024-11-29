from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="settings"
    )
    phone_number = models.CharField(
        max_length=15, blank=True
    )  # Добавляем поле телефона
    company_name = models.CharField(max_length=255, blank=True)
    owner_name = models.CharField(max_length=255, blank=True)
    new_order_notifications = models.BooleanField(default=True)
    order_status_notifications = models.BooleanField(default=True)
    financial_notifications = models.BooleanField(default=True)
    telegram_connected = models.BooleanField(default=False)
    telegram_chat_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Настройка у {self.user.username}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_settings(sender, instance, created, **kwargs):
    if created:
        UserSettings.objects.create(user=instance)
