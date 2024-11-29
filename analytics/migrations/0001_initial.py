# Generated by Django 5.1.2 on 2024-11-13 14:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('goods', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PeriodicReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period_start', models.DateField()),
                ('period_end', models.DateField()),
                ('total_quantity_sold', models.PositiveIntegerField()),
                ('total_revenue', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_profit', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('profit_margin', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('avg_profit_margin', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('avg_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='goods.category')),
            ],
            options={
                'verbose_name': 'Периодический отчет',
                'verbose_name_plural': 'Периодические отчеты',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='SalesRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('quantity_sold', models.PositiveIntegerField()),
                ('sale_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cost_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('profit', models.DecimalField(decimal_places=2, max_digits=10)),
                ('profit_margin', models.DecimalField(decimal_places=2, max_digits=5)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='goods.category')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales_records', to='goods.product')),
            ],
            options={
                'verbose_name': 'Продажа',
                'verbose_name_plural': 'Продаж',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DiscountRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount_type', models.CharField(max_length=50)),
                ('discount_value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.DateTimeField()),
                ('product_name', models.CharField(max_length=255)),
                ('product_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity_sold', models.PositiveIntegerField()),
                ('final_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('sales_record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discounts', to='analytics.salesrecord')),
            ],
        ),
        migrations.CreateModel(
            name='SalesTrend',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(db_index=True)),
                ('month', models.IntegerField(db_index=True)),
                ('total_quantity_sold', models.PositiveIntegerField()),
                ('total_revenue', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_profit', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('profit_margin', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='goods.category')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales_trends', to='goods.product')),
            ],
            options={
                'verbose_name': 'Тренд продаж',
                'verbose_name_plural': 'Тренды продаж',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='StockHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('quantity_change', models.IntegerField()),
                ('change_type', models.CharField(max_length=100)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock_histories', to='goods.product')),
            ],
            options={
                'verbose_name': 'История изменений',
                'verbose_name_plural': 'Истории изменений',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='UserSalesAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_quantity', models.PositiveIntegerField()),
                ('total_revenue', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_profit', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('avg_profit_margin', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('last_purchase_date', models.DateTimeField(null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_sales', to='goods.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales_analyses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Анализ продаж',
                'verbose_name_plural': 'Анализы продаж',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DailySalesReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_index=True)),
                ('total_sales', models.PositiveIntegerField(default=0)),
                ('total_revenue', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_orders', models.PositiveIntegerField(default=0)),
                ('average_order_value', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('best_selling_product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='daily_best_sales', to='goods.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_sales_reports', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Ежедневный отчет о продажах',
                'verbose_name_plural': 'Ежедневные отчеты о продажах',
                'ordering': ['-date'],
                'managed': True,
                'unique_together': {('user', 'date')},
            },
        ),
    ]
