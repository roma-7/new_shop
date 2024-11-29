import logging
from typing import Dict, Any
from decimal import Decimal
from django.conf import settings
import telebot
from analytics.models import DailySalesReport
from .models import TelegramUserProfile

logger = logging.getLogger(__name__)


class AnalyticsNotificationService:
    def __init__(self):
        self.bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)

    def format_daily_report(self, report: DailySalesReport) -> str:
        """Форматирует ежедневный отчет в читаемое сообщение."""
        message = f"📊 Отчет по продажам за {report.date}\n\n"

        # Основные метрики
        message += f"💰 Общая выручка: {report.total_revenue:,.2f}₽\n"
        message += f"📦 Всего продаж: {report.total_sales}\n"
        message += f"🛍 Количество заказов: {report.total_orders}\n"

        if report.average_order_value:
            message += f"💎 Средний чек: {report.average_order_value:,.2f}₽\n"

        if report.best_selling_product:
            message += (
                f"\n🏆 Лучший товар: {report.best_selling_product.product_name}\n"
            )

        # Сравнение с предыдущим днем
        previous_report = report.get_previous_day_stats()
        if previous_report:
            revenue_change = (
                (report.total_revenue - previous_report.total_revenue)
                / previous_report.total_revenue
                * 100
                if previous_report.total_revenue
                else 0
            )
            sales_change = (
                (report.total_sales - previous_report.total_sales)
                / previous_report.total_sales
                * 100
                if previous_report.total_sales
                else 0
            )

            message += f"\n📈 Изменения по сравнению со вчера:\n"
            message += f"Выручка: {revenue_change:+.1f}%\n"
            message += f"Продажи: {sales_change:+.1f}%\n"

        return message

    def send_daily_report(self, user_id: int) -> bool:
        """Отправляет ежедневный отчет пользователю через Telegram."""
        try:
            # Получаем профиль пользователя с chat_id
            profile = TelegramUserProfile.objects.select_related("user").get(
                user_id=user_id, is_active=True
            )

            # Получаем последний отчет
            report = (
                DailySalesReport.objects.filter(user_id=user_id)
                .select_related("best_selling_product")
                .first()
            )

            if not report:
                logger.warning(f"No daily report found for user {user_id}")
                return False

            # Форматируем и отправляем сообщение
            message = self.format_daily_report(report)
            self.bot.send_message(
                chat_id=profile.telegram_chat_id, text=message, parse_mode="HTML"
            )

            logger.info(f"Successfully sent daily report to user {user_id}")
            return True

        except TelegramUserProfile.DoesNotExist:
            logger.error(f"Telegram profile not found for user {user_id}")
            return False
        except Exception as e:
            logger.error(f"Error sending notification to user {user_id}: {str(e)}")
            return False

    def send_bulk_daily_reports(self):
        """Отправляет ежедневные отчеты всем активным пользователям."""
        active_profiles = TelegramUserProfile.objects.filter(is_active=True)

        for profile in active_profiles:
            self.send_daily_report(profile.user_id)
