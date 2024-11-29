from django.db import models
from django.contrib.auth.models import User


class TelegramUserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="telegram_profile"
    )
    telegram_chat_id = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Telegram профиль {self.user.username}"

    def save(self, *args, **kwargs):
        # Убедимся, что chat_id сохраняется
        if self.telegram_chat_id:
            self.telegram_chat_id = str(self.telegram_chat_id)
        super().save(*args, **kwargs)
