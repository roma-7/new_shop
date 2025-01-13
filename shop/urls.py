from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("users.urls", namespace="users")),
    path("goods/", include("goods.urls", namespace="goods")),
    path("main/", include("main.urls", namespace="main")),
    path("notification/", include("notification.urls", namespace="notification")),
    path("analytics/", include("analytics.urls", namespace="analytics")),
] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_URL)
