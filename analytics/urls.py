from django.urls import path
from . import views

app_name = "analytics"

urlpatterns = [
    # Основная страница аналитики
    path("", views.analytics, name="dashboard"),
    # Список продаж
    path("sales/", views.sales_list, name="sales_list"),
    # Тренды продаж
    path("trends/", views.sales_trends, name="sales_trends"),
    # Анализ продаж пользователя
    path("analysis/", views.user_sales_analysis, name="user_analysis"),
    # Периодический отчет
    path("report/", views.periodic_report, name="periodic_report"),
    
    path("daily/", views.daily_sales_report, name="daily_sales_report"),
    
    path("low-stock/", views.low_stock_products, name="low_stock_products"),
    
    path("discounts/", views.discount_records, name="discount_records"),
]
