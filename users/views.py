from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from allauth.account.forms import ChangePasswordForm

from goods.models import Product

from .forms import CustomSignupForm, ProfileSettingsForm
from .models import UserSettings
from django.conf import settings as django_settings


from analytics.models import (
    SalesRecord,
)
from django.utils import timezone
from django.db.models import Sum, Avg, Count, F
from datetime import timedelta
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay


@login_required
def settings_view(request):
    user_settings, created = UserSettings.objects.get_or_create(user=request.user)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "save_settings":
            settings_form = ProfileSettingsForm(request.POST)
            if settings_form.is_valid():
                # Обновляем данные пользователя
                request.user.first_name = settings_form.cleaned_data["first_name"]
                request.user.last_name = settings_form.cleaned_data["last_name"]
                request.user.save()

                # Обновляем настройки пользователя
                user_settings.phone_number = settings_form.cleaned_data["phone_number"]
                user_settings.company_name = settings_form.cleaned_data["company_name"]
                user_settings.owner_name = settings_form.cleaned_data["owner_name"]

                # Обновляем настройки уведомлений
                user_settings.new_order_notifications = (
                    request.POST.get("new_order_notifications") == "on"
                )
                user_settings.order_status_notifications = (
                    request.POST.get("order_status_notifications") == "on"
                )
                user_settings.financial_notifications = (
                    request.POST.get("financial_notifications") == "on"
                )

                user_settings.save()
                messages.success(request, "Настройки успешно сохранены")
                return redirect("users:settings")
            else:
                messages.error(request, "Пожалуйста, исправьте ошибки в форме")

        elif action == "change_password":
            password_form = ChangePasswordForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, "Пароль успешно изменен")
                return redirect("users:settings")
            else:
                messages.error(
                    request, "Пожалуйста, исправьте ошибки в форме смены пароля"
                )

    # Для GET запроса
    initial_data = {
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "phone_number": user_settings.phone_number,
        "company_name": user_settings.company_name,
        "owner_name": user_settings.owner_name,
    }
    settings_form = ProfileSettingsForm(initial=initial_data)
    password_form = ChangePasswordForm(user=request.user)

    context = {
        "settings_form": settings_form,
        "password_form": password_form,
        "user_settings": user_settings,
        "telegram_bot_username": getattr(
            django_settings, "TELEGRAM_BOT_USERNAME", None
        ),
    }

    return render(request, "users/settings_users.html", context)


class StartMenuView(TemplateView):
    template_name = "users/start_menu.html"


@login_required
def registered_user_view(request):
    return render(request, "home.html", {"is_registered": True})


def unregistered_user_view(request):
    return render(request, "login.html", {"is_registered": False})


@login_required
def control_panel_user_view(request):
    user_settings, created = UserSettings.objects.get_or_create(user=request.user)
    latest_products = (
        Product.objects.filter(author=request.user)
        .select_related("model", "model__category")
        .prefetch_related("images")
        .order_by("-id")[:5]
    )

    context = {
        "user_data": {
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "phone_number": user_settings.phone_number,
            "company_name": user_settings.company_name,
            "owner_name": user_settings.owner_name,
        },
        "user_settings": user_settings,
        "latest_products": latest_products,
    }

    return render(request, "users/control_panel_users.html", context)


@login_required
def analyst_dashboard(request):
    # Получаем выбранный период (по умолчанию 30 дней)
    selected_period = request.GET.get("period", "30")
    period_days = int(selected_period)

    # Вычисляем дату начала периода
    start_date = timezone.now() - timedelta(days=period_days)

    user_settings, created = UserSettings.objects.get_or_create(user=request.user)

    # Базовый queryset для продаж
    base_sales = SalesRecord.objects.filter(
        product__author=request.user, date__gte=start_date
    )

    # Определяем группировку и форматирование в зависимости от периода
    if selected_period == "7":
        sales_over_time = (
            base_sales.annotate(period=TruncDay("date"))
            .values("period")
            .annotate(revenue=Sum(F("quantity_sold") * F("sale_price")))
            .order_by("period")
        )

        formatted_data = [
            {
                "month": item["period"].strftime("%d-%m"),
                "revenue": float(item["revenue"]),
            }
            for item in sales_over_time
        ]

    elif selected_period == "30":
        sales_over_time = (
            base_sales.annotate(period=TruncWeek("date"))
            .values("period")
            .annotate(revenue=Sum(F("quantity_sold") * F("sale_price")))
            .order_by("period")
        )

        formatted_data = [
            {
                "month": f"Неделя {(item['period'].day // 7) + 1}",
                "revenue": float(item["revenue"]),
            }
            for item in sales_over_time
        ]

    else:  # 90 дней
        sales_over_time = (
            base_sales.annotate(period=TruncMonth("date"))
            .values("period")
            .annotate(revenue=Sum(F("quantity_sold") * F("sale_price")))
            .order_by("period")
        )

        formatted_data = [
            {"month": item["period"].strftime("%b"), "revenue": float(item["revenue"])}
            for item in sales_over_time
        ]

    # Статистика по сравнению с предыдущим периодом
    previous_start = start_date - timedelta(days=period_days)
    previous_revenue = (
        base_sales.filter(date__gte=previous_start, date__lt=start_date).aggregate(
            revenue=Sum(F("quantity_sold") * F("sale_price"))
        )["revenue"]
        or 0
    )

    current_revenue = (
        base_sales.aggregate(revenue=Sum(F("quantity_sold") * F("sale_price")))[
            "revenue"
        ]
        or 0
    )

    revenue_trend = (
        ((current_revenue - previous_revenue) / previous_revenue * 100)
        if previous_revenue > 0
        else 0
    )

    total_orders = base_sales.count()
    sales_data = {
        "total_revenue": current_revenue,
        "revenue_trend": revenue_trend,
        "total_orders": total_orders,
        "orders_trend": 0,
        "avg_order": current_revenue / total_orders if total_orders > 0 else 0,
        "avg_order_trend": 0,
    }

    # Топ-5 популярных товаров
    popular_products = (
        base_sales.values("product__product_name")
        .annotate(total_revenue=Sum(F("quantity_sold") * F("sale_price")))
        .order_by("-total_revenue")[:5]
    )

    # Объединяем все данные в один контекст
    context = {
        "selected_period": selected_period,
        "sales_data": sales_data,
        "monthly_revenue": formatted_data,
        "popular_products": popular_products,
        "user_data": {
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "phone_number": user_settings.phone_number,
            "company_name": user_settings.company_name,
            "owner_name": user_settings.owner_name,
        },
        "user_settings": user_settings,
    }

    return render(request, "users/analyst_users.html", context)


@login_required
def product_users_view(request):
    user_settings, created = UserSettings.objects.get_or_create(user=request.user)
    initial_data = {
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "phone_number": user_settings.phone_number,
        "company_name": user_settings.company_name,
        "owner_name": user_settings.owner_name,
    }
    settings_form = CustomSignupForm(initial=initial_data)

    context = {
        "settings_form": settings_form,
        "user_settings": user_settings,
    }
    return render(request, "users/product_users.html", context)
