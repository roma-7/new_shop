from django.core.management.base import BaseCommand
from notification.services import AnalyticsNotificationService


class Command(BaseCommand):
    help = "Отправляет ежедневные отчеты всем пользователям через Telegram"

    def handle(self, *args, **options):
        service = AnalyticsNotificationService()
        service.send_bulk_daily_reports()
        self.stdout.write(self.style.SUCCESS("Successfully sent daily reports"))
