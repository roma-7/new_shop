# signals.py
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SalesRecord, UserSalesAnalysis, PeriodicReport


@receiver(post_save, sender=SalesRecord)
def update_analytics(sender, instance, created, **kwargs):
    if created:
        # Обновляем UserSalesAnalysis
        analysis, _ = UserSalesAnalysis.objects.get_or_create(
            user=instance.product.author,
            product=instance.product,
            defaults={
                "total_quantity": 0,
                "total_revenue": 0,
                "total_cost": 0,
                "total_profit": 0,
                "avg_profit_margin": 0,
                "last_purchase_date": instance.date,
            },
        )

        analysis.total_quantity += instance.quantity_sold
        analysis.total_revenue += instance.quantity_sold * instance.sale_price
        analysis.total_cost += instance.quantity_sold * instance.cost_price
        analysis.total_profit += instance.profit
        
        # Обновляем среднюю маржинальность
        if analysis.total_revenue > 0:
            analysis.avg_profit_margin = (analysis.total_profit / analysis.total_revenue) * 100
            
        analysis.last_purchase_date = instance.date
        analysis.save()

        # Обновляем PeriodicReport
        report, _ = PeriodicReport.objects.get_or_create(
            period_start=instance.date.date().replace(day=1),
            period_end=instance.date.date().replace(day=1) + timedelta(days=32),
            category=instance.category,
            defaults={
                "total_quantity_sold": 0,
                "total_revenue": 0,
                "total_cost": 0,
                "total_profit": 0,
                "avg_price": 0,
                "avg_profit_margin": 0
            },
        )

        report.total_quantity_sold += instance.quantity_sold
        report.total_revenue += instance.quantity_sold * instance.sale_price
        report.total_cost += instance.quantity_sold * instance.cost_price
        report.total_profit += instance.profit
        report.avg_price = report.total_revenue / report.total_quantity_sold
        
        if report.total_revenue > 0:
            report.avg_profit_margin = (report.total_profit / report.total_revenue) * 100
            
        report.save()


from django.utils import timezone
from .models import DailySalesReport
from django.db.models import Sum
from django.db import transaction


@receiver(post_save, sender=SalesRecord)
@transaction.atomic
def update_daily_sales(sender, instance, created, **kwargs):
    if created:
        today = timezone.now().date()
        user = instance.product.author  # Получаем автора продукта

        daily_report, created = DailySalesReport.objects.get_or_create(
            user=user,
            date=today,
            defaults={"total_sales": 0, "total_revenue": 0, "total_orders": 0},
        )

        # Обновляем статистику
        daily_report.total_sales += instance.quantity_sold
        daily_report.total_revenue += instance.quantity_sold * instance.sale_price
        daily_report.total_orders += 1

        # Обновляем среднюю стоимость заказа
        daily_report.update_average_order_value()

        # Определяем самый продаваемый продукт для конкретного пользователя
        best_product = (
            SalesRecord.objects.filter(
                date__date=today, product__author=user  # Фильтруем по автору
            )
            .values("product")
            .annotate(total_qty=Sum("quantity_sold"))
            .order_by("-total_qty")
            .first()
        )

        if best_product:
            daily_report.best_selling_product_id = best_product["product"]

        daily_report.save()
