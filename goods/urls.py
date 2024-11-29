from django.urls import path

from . import views
from .views import *

app_name = "goods"

urlpatterns = [
    path('categories/', views.categories_view, name='categories'),
    path('category/<int:category_id>/models/', views.phone_models_view, name='phone_models'),
    path('category/<int:category_id>/model/<int:phone_model_id>/products/', 
         views.product_catalog, name='product_catalog'),
    path("products/create/", views.create_product, name="create_product"),
    path('catalog/', views.product_catalog, name='product_catalog'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('sell/<int:product_id>/', views.sell_product, name='sell_product'),
    path("error/", views.error, name="error"),
    path("api/get_phone_models/<int:category_id>/", views.get_phone_models, name="get_phone_models"),
    path("api/get_product_models/<int:category_id>/<int:phone_model_id>/", views.get_product_models, name="get_product_models"),
    path('product/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('product/<int:pk>/delete/', views.delete_product, name='delete_product'),

]
