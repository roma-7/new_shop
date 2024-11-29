# goods/forms.py
from django import forms
from .models import Product, ProductImage


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "product_name",
            "description",
            "cost_price",
            "price",
            "custom_discount",
            "quantity",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "product_name": forms.TextInput(attrs={"class": "form-input"}),
            "cost_price": forms.NumberInput(attrs={"class": "form-input"}),
            "price": forms.NumberInput(attrs={"class": "form-input"}),
            "custom_discount": forms.NumberInput(attrs={"class": "form-input"}),
            "quantity": forms.NumberInput(attrs={"class": "form-input"}),
        }


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ["image_front"]
        widgets = {"image_front": forms.FileInput(attrs={"class": "form-input"})}
