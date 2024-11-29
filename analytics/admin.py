from django.contrib import admin
from .models import (
    SalesRecord,
    StockHistory,
    SalesTrend,
    UserSalesAnalysis,
    PeriodicReport,
    DailySalesReport,
    DiscountRecord
)


admin.site.register(SalesRecord)
admin.site.register(StockHistory)
admin.site.register(SalesTrend)
admin.site.register(UserSalesAnalysis)
admin.site.register(PeriodicReport)
admin.site.register(DailySalesReport)
admin.site.register(DiscountRecord)