# urls.py
from django.urls import path
from . import views

app_name = "notification"

urlpatterns = [
    path("connect/", views.connect_telegram, name="connect_telegram"),
]
