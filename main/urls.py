from django.urls import path
from .views import *

app_name= "main"

urlpatterns = [
    path("about/", about_us, name="about"),
    path("faq/", faq, name="faq"),
]
