import os
from celery import Celery
from celery.schedules import crontab


# Устанавливаем путь к настройкам Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shop.settings")
# Создание объекта Celery
app = Celery("shop")

# Настройки Celery
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автозагрузка задач
app.autodiscover_tasks()

# Настройка периодичности задач
app.conf.beat_schedule = {
    "send-daily-reports": {
        "task": "notification.tasks.send_daily_analytics_reports",
        "schedule": crontab(minute=30, hour=23),  # Запуск каждый день в 22:30
    },
}

# Обработка ошибок и уведомлений
app.conf.timezone = "Asia/Bishkek"
