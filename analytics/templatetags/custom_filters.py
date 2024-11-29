# templatetags/custom_filters.py
import decimal
from django import template
from decimal import Decimal


register = template.Library()


@register.filter
def multiply(value, arg):
    return float(value) * float(arg)


@register.filter
def subtract(value, arg):
    return float(value) - float(arg)




@register.filter
def sum_attr(queryset, attr):
    return sum(getattr(obj, attr) for obj in queryset)


@register.filter
def avg_revenue(queryset):
    if not queryset:
        return 0
    total_revenue = sum(obj.total_revenue for obj in queryset)
    total_quantity = sum(obj.total_quantity for obj in queryset)
    return total_revenue / total_quantity if total_quantity else 0


@register.filter
def divide(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0


@register.filter
def multiply(value, arg):
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except (ValueError, TypeError, decimal.InvalidOperation):
        return 0


@register.filter
def divide(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0
