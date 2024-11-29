from django.urls import path
from . import views

from .views import *


app_name = "users"


urlpatterns = [
    path("", StartMenuView.as_view()),
    path("profile/settings/", settings_view, name="settings"),
    path("profile/analytics/", views.analyst_dashboard, name="analyst"),
    path("profile/control-panel/", control_panel_user_view, name="control-panel"),
]
