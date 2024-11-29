from decimal import Decimal
import logging
from django.db.models import F, Sum, Avg, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncMonth
from django.db.models.functions import ExtractYear, ExtractMonth
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg
from django.utils import timezone
from datetime import timedelta

from analytics.models import (
    SalesRecord,
    StockHistory,
    SalesTrend,
    UserSalesAnalysis,
    PeriodicReport,
    DailySalesReport,
    DiscountRecord,
    
)
from goods.models import Product
from django.db.models import Q


def analytics(request):
    return render(request, "analytics/dashboard.html")


# 1. Список продаж для текущего пользователя
import logging
logger = logging.getLogger(__name__)

@login_required
def sales_list(request):
    sales = SalesRecord.objects.filter(product__author=request.user).select_related(
        'product', 
        'category'
    ).order_by("-date")[:20]
    
    # Добавьте отладочную информацию
    for sale in sales:
        logger.debug(f"Sale ID: {sale.id}, Product: {sale.product}, Category: {sale.category}")
    
    return render(request, "analytics/sales_list.html", {"sales": sales})


# 3. Тренды продаж за последние 30 дней для текущего пользователя

from decimal import Decimal
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Avg, F, ExpressionWrapper, DecimalField , Count
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

@login_required
def sales_trends(request):
    """
    Отображает тренды продаж за последние 30 дней с агрегированной статистикой.
    """
    try:
        # Получаем период для анализа
        last_30_days = timezone.now() - timedelta(days=30)

        # Получаем продажи с оптимизированными запросами
        sales_data = (
            SalesRecord.objects.filter(
                product__author=request.user, date__gte=last_30_days
            )
            .values(
                "product_id",
                "product__product_name",
                "product__model__model_name",  # Добавляем название модели
            )
            .annotate(
                total_quantity=Sum("quantity_sold"),
                total_revenue=Sum(F("quantity_sold") * F("sale_price")),
                total_cost=Sum(F("quantity_sold") * F("cost_price")),
                total_profit=Sum("profit"),
                average_price=ExpressionWrapper(
                    Sum(F("quantity_sold") * F("sale_price")) / Sum("quantity_sold"),
                    output_field=DecimalField(),
                ),
                sales_count=Count("id"),
            )
            .order_by("-total_revenue")
        )

        # Получаем тренды за текущий месяц
        current_month = timezone.now().month
        current_year = timezone.now().year

        # Обновляем или создаем тренды
        trends = []
        for data in sales_data:
            try:
                trend, created = SalesTrend.objects.update_or_create(
                    product_id=data['product_id'],
                    year=current_year,
                    month=current_month,
                    defaults={
                        'total_quantity_sold': data['total_quantity'],
                        'total_revenue': data['total_revenue'],
                        'total_cost': data['total_cost'],
                        'total_profit': data['total_profit'],
                    }
                )

                # Вычисляем рост по сравнению с прошлым месяцом
                prev_month = current_month - 1 if current_month > 1 else 12
                prev_year = current_year if current_month > 1 else current_year - 1

                prev_trend = SalesTrend.objects.filter(
                    product_id=data['product_id'],
                    year=prev_year,
                    month=prev_month
                ).first()

                growth = calculate_growth(
                    current_value=data['total_quantity'],
                    previous_value=prev_trend.total_quantity_sold if prev_trend else 0
                )

                trends.append({
                    'product_name': data['product__product_name'],
                    'model_name': data['product__model__model_name'],
                    'total_quantity': data['total_quantity'],
                    'total_revenue': data['total_revenue'],
                    'total_profit': data['total_profit'],
                    'average_price': data['average_price'],
                    'growth': growth,
                    'sales_count': data['sales_count']
                })

            except Exception as e:
                logger.error(f"Error processing trend for product {data['product_id']}: {str(e)}")
                continue

        # Подготавливаем общую статистику
        if trends:
            total_stats = {
                'total_revenue': sum(t['total_revenue'] for t in trends),
                'total_profit': sum(t['total_profit'] for t in trends),
                'total_quantity': sum(t['total_quantity'] for t in trends),
                'average_growth': sum(float(t['growth']) for t in trends) / len(trends)
            }
        else:
            total_stats = {
                'total_revenue': Decimal('0.00'),
                'total_profit': Decimal('0.00'),
                'total_quantity': 0,
                'average_growth': 0
            }

        context = {
            'trends': trends,
            'total_stats': total_stats,
            'period_start': last_30_days.date(),
            'period_end': timezone.now().date(),
        }

        logger.info(f"Successfully generated sales trends for {len(trends)} products")
        return render(request, 'analytics/sales_trends.html', context)

    except Exception as e:
        logger.error(f"Error in sales_trends view: {str(e)}", exc_info=True)
        return render(request, 'analytics/sales_trends.html', {
            'error': 'Произошла ошибка при формировании трендов продаж',
            'trends': []
        })

def calculate_growth(current_value, previous_value):
    """
    Вычисляет процент роста между двумя значениями.
    """
    try:
        if not previous_value:
            return Decimal('0.00')
        return ((current_value - previous_value) / previous_value * 100).quantize(Decimal('0.01'))
    except Exception:
        return Decimal('0.00')


# 4. Анализ продаж по текущему пользователю
@login_required
def user_sales_analysis(request):
    user_analyses = (
        UserSalesAnalysis.objects.filter(user=request.user)
        .select_related("product")
        .annotate(
            total_sales=Sum("total_quantity"),
            total_revenue_sum=Sum("total_revenue"),
            avg_price=ExpressionWrapper(
                F("total_revenue") / F("total_quantity"), output_field=DecimalField()
            ),
        )
        .order_by("-total_revenue")
    )

    context = {
        "user_analyses": user_analyses,
        "total_revenue": user_analyses.aggregate(Sum("total_revenue"))[
            "total_revenue__sum"
        ],
        "total_quantity": user_analyses.aggregate(Sum("total_quantity"))[
            "total_quantity__sum"
        ],
        "avg_revenue": user_analyses.aggregate(avg_revenue=Avg("total_revenue"))[
            "avg_revenue"
        ],
    }

    return render(request, "analytics/user_sales_analysis.html", context)


# 5. Отчет по продажам за выбранный период для текущего пользователя@login_required
@login_required
def periodic_report(request):
    period_start = request.GET.get("start_date")
    period_end = request.GET.get("end_date")

    if period_start and period_end:
        # Получаем продажи за выбранный период
        sales = SalesRecord.objects.filter(
            product__author=request.user,
            date__date__gte=period_start,
            date__date__lte=period_end,
        ).select_related("category")

        reports_data = {}
        for sale in sales:
            key = sale.category.id if sale.category else 0
            if key not in reports_data:
                reports_data[key] = {
                    "category": sale.category,
                    "total_quantity_sold": 0,
                    "total_revenue": Decimal("0.00"),
                    "total_cost": Decimal("0.00"),
                    "total_profit": Decimal("0.00"),
                    "sales_count": 0,
                }
            
            # Обновляем данные для каждой категории
            reports_data[key]["total_quantity_sold"] += sale.quantity_sold
            reports_data[key]["total_revenue"] += sale.quantity_sold * sale.sale_price
            reports_data[key]["total_cost"] += sale.quantity_sold * sale.cost_price
            reports_data[key]["total_profit"] += sale.profit
            reports_data[key]["sales_count"] += 1

        # Создаем или обновляем отчеты
        reports = []
        for data in reports_data.values():
            # Рассчитываем маржу для категории
            revenue = data["total_revenue"]
            profit = data["total_profit"]
            profit_margin = (profit / revenue * 100) if revenue > 0 else 0

            report = PeriodicReport.objects.create(
                period_start=period_start,
                period_end=period_end,
                category=data["category"],
                total_quantity_sold=data["total_quantity_sold"],
                total_revenue=data["total_revenue"],
                total_cost=data["total_cost"],
                total_profit=data["total_profit"],
                profit_margin=profit_margin,
                avg_price=(
                    data["total_revenue"] / data["total_quantity_sold"]
                    if data["total_quantity_sold"] > 0
                    else 0
                ),
            )
            reports.append(report)

        # Подготавливаем агрегированные данные
        total_revenue = sum(r.total_revenue for r in reports)
        total_cost = sum(r.total_cost for r in reports)
        total_profit = sum(r.total_profit for r in reports)
        
        total_data = {
            "total_sales": sum(r.total_quantity_sold for r in reports),
            "revenue_sum": total_revenue,
            "total_cost": total_cost,
            "total_profit": total_profit,
            "average_price": (
                total_revenue / sum(r.total_quantity_sold for r in reports)
                if reports and sum(r.total_quantity_sold for r in reports) > 0
                else 0
            ),
            "average_profit_margin": (
                (total_profit / total_revenue * 100)
                if total_revenue > 0
                else 0
            ),
        }

        context = {
            "reports": reports,
            "total_data": total_data,
            "start_date": period_start,
            "end_date": period_end,
        }
    else:
        context = {"reports": [], "start_date": period_start, "end_date": period_end}

    return render(request, "analytics/periodic_report.html", context)


@login_required
def daily_sales_report(request):
    today = timezone.now().date()

    # Получаем отчет только для текущего пользователя
    daily_report = DailySalesReport.objects.filter(
        user=request.user, date=today
    ).first()

    if not daily_report:
        daily_report = DailySalesReport.objects.create(user=request.user, date=today)

    previous_day = daily_report.get_previous_day_stats()

    # Получаем предыдущие отчеты только для текущего пользователя
    context = {
        "report": daily_report,
        "previous_day": previous_day,
        "previous_reports": DailySalesReport.objects.filter(user=request.user)
        .exclude(date=today)
        .order_by("-date")[:7],
    }

    return render(request, "analytics/daily_sales_report.html", context)


@login_required
def low_stock_products(request):
    """
    Отображает товары, у которых количество меньше 10 штук
    """
    low_stock_items = Product.objects.filter(author=request.user,quantity__lt=10).select_related("model")

    total_products = Product.objects.filter(author=request.user).count()
    low_stock_count = low_stock_items.count()

    context = {
        "low_stock_items": low_stock_items,
        "total_products": total_products,
        "low_stock_count": low_stock_count,
        "stock_threshold": 10,
    }

    return render(request, "analytics/low_stock.html", context)


@login_required
def discount_records(request):
    discounts = DiscountRecord.objects.filter(sales_record__product__author=request.user)
    
    # Фильтрация по поиску
    search_query = request.GET.get('search', '')
    if search_query:
        discounts = discounts.filter(
            Q(product_name__icontains=search_query) |
            Q(discount_type__icontains=search_query)
        )
    
    # Фильтрация по дате
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        discounts = discounts.filter(date__gte=start_date)
    if end_date:
        discounts = discounts.filter(date__lte=end_date + " 23:59:59")
    
    # Сортировка
    sort_by = request.GET.get('sort', '-date')  # По умолчанию сортировка по дате (свежие первые)
    discounts = discounts.order_by(sort_by)
    
    # Подсчёт общих значений
    total_sales = sum(discount.final_price for discount in discounts)
    total_discounts = sum(discount.discount_value for discount in discounts)
    total_quantity = sum(discount.quantity_sold for discount in discounts)
    avg_discount = total_discounts / len(discounts) if discounts else 0
    
    context = {
        'discounts': discounts,
        'total_sales': total_sales,
        'total_discounts': total_discounts,
        'total_quantity': total_quantity,
        'avg_discount': avg_discount,
        'search_query': search_query,
        'start_date': start_date,
        'end_date': end_date,
        'sort_by': sort_by,
    }
    
    return render(request, 'analytics/discount_records.html', context)
