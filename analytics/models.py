from datetime import timedelta
from django.utils import timezone
from django.db import models
from goods.models import Product, Category
from django.contrib.auth.models import User


# 1. Модель для хранения данных о продажах
class SalesRecord(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sales_records")
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    quantity_sold = models.PositiveIntegerField()
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)  # Добавляем поле себестоимости
    profit = models.DecimalField(max_digits=10, decimal_places=2)      # Добавляем поле прибыли
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2)  # Добавляем маржинальность в %
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.cost_price and self.product:
            self.cost_price = self.product.cost_price
        self.profit = (self.sale_price - self.cost_price) * self.quantity_sold
        if self.sale_price > 0:
            self.profit_margin = ((self.sale_price - self.cost_price) / self.sale_price) * 100
        super().save(*args, **kwargs)

    class Meta:
        managed = True
        verbose_name = "Продажа"
        verbose_name_plural = "Продаж"

    def __str__(self):
        return f"Продажа {self.product} на {self.date} | {self.category}"


class DiscountRecord(models.Model):
    sales_record = models.ForeignKey(
        SalesRecord, on_delete=models.CASCADE, related_name="discounts"
    )
    discount_type = models.CharField(max_length=50)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField()
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_sold = models.PositiveIntegerField()
    final_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Скидка {self.discount_value} ({self.discount_type}) для {self.product_name}"


# 2. Модель для истории изменений остатков на складе
class StockHistory(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="stock_histories"
    )
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    quantity_change = models.IntegerField()  # Положительное или отрицательное значение
    change_type = models.CharField(
        max_length=100
    )  # Причина изменения, например "продажа", "пополнение"

    class Meta:
        managed = True
        verbose_name = "История изменений"
        verbose_name_plural = "Истории изменений"

    def __str__(self):
        return f"Изменение запасов для {self.product} на {self.date}: {self.quantity_change}"


# 3. Модель для анализа трендов продаж на длительный период
class SalesTrend(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="sales_trends"
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    year = models.IntegerField(db_index=True)
    month = models.IntegerField(db_index=True)
    total_quantity_sold = models.PositiveIntegerField()
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        managed = True
        verbose_name = "Тренд продаж"
        verbose_name_plural = "Тренды продаж"

    def __str__(self):
        return f"Тренд продаж для {self.product} в {self.month}/{self.year}"


# 4. Модель для аналитики продаж по пользователям
class UserSalesAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sales_analyses")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="user_sales")
    total_quantity = models.PositiveIntegerField()
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)    # Добавляем общую себестоимость
    total_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Добавляем общую прибыль
    avg_profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Добавляем среднюю маржинальность
    last_purchase_date = models.DateTimeField(null=True)
    
    class Meta:
        managed = True
        verbose_name = "Анализ продаж"
        verbose_name_plural = "Анализы продаж"

    def __str__(self):
        return f"Анализ продаж пользователя {self.user.username}"


# 5. Модель для отчетов по периодам
class PeriodicReport(models.Model):
    period_start = models.DateField()
    period_end = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    total_quantity_sold = models.PositiveIntegerField()
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_profit_margin = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    avg_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = True
        verbose_name = 'Периодический отчет'
        verbose_name_plural = 'Периодические отчеты'

    def __str__(self):
        return f"Периодический отчет с {self.period_start} по {self.period_end}"


class DailySalesReport(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="daily_sales_reports"
    )
    date = models.DateField(db_index=True)
    total_sales = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    best_selling_product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, related_name="daily_best_sales"
    )
    total_orders = models.PositiveIntegerField(default=0)
    average_order_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        verbose_name = "Ежедневный отчет о продажах"
        verbose_name_plural = "Ежедневные отчеты о продажах"
        ordering = ["-date"]
        unique_together = [
            "user",
            "date",
        ]  # Добавляем уникальность по пользователю и дате

    def __str__(self):
        return f"Отчет за {self.date}: {self.total_sales} продаж (Пользователь: {self.user.username})"

    def update_average_order_value(self):
        if self.total_orders > 0:
            self.average_order_value = self.total_revenue / self.total_orders
        else:
            self.average_order_value = 0

    def get_previous_day_stats(self):
        previous_day = timezone.now().date() - timedelta(days=1)
        return DailySalesReport.objects.filter(
            user=self.user, date=previous_day
        ).first()
