from celery import shared_task

from .services import AnalyticsNotificationService


@shared_task
def send_daily_analytics_reports():
    """Celery задача для отправки ежедневных отчетов."""
    service = AnalyticsNotificationService()
    service.send_bulk_daily_reports()


