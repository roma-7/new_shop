from django.contrib import admin
from django.utils.html import format_html
from .models import Category, PhoneModel, ProductModel, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("category_name", "total_phone_models")
    search_fields = ("category_name",)

    def total_phone_models(self, obj):
        return obj.phone_models.count()

    total_phone_models.short_description = "Количество моделей телефонов"


@admin.register(PhoneModel)
class PhoneModelAdmin(admin.ModelAdmin):
    list_display = ("phone_name", "category", "total_product_models")
    list_filter = ("category",)
    search_fields = ("phone_name", "category__category_name")

    def total_product_models(self, obj):
        return obj.models.count()

    total_product_models.short_description = "Количество моделей"


@admin.register(ProductModel)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ("model_name", "phone_model", "total_products")
    list_filter = ("category__category",)
    search_fields = ("model_name", "category__phone_name")

    def phone_model(self, obj):
        return obj.category.phone_name

    phone_model.short_description = "Модель телефона"

    def total_products(self, obj):
        return obj.product_set.count()

    total_products.short_description = "Количество товаров"


# class ProductImageInline(admin.TabularInline):
#     model = ProductImage
#     extra = 2
#     readonly_fields = ("preview_front", "preview_back")

#     def preview_front(self, obj):
#         return self.preview_image(obj.image_front)

#     preview_front.short_description = "Предпросмотр (спереди)"

#     def preview_back(self, obj):
#         return self.preview_image(obj.image_back)

#     preview_back.short_description = "Предпросмотр (сзади)"

#     def preview_image(self, image):
#         if image:
#             return format_html(
#                 '<img src="{}" style="max-width:200px; max-height:200px;" />', image.url
#             )
#         return "Нет изображения"


# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = (
#         "product_name",
#         "author",
#         "model",
#         "price",
#         "quantity",
#         "total_images",
#     )
#     list_filter = ("author", "model__category", "model")
#     search_fields = ("product_name", "description", "author__username")
#     inlines = [ProductImageInline]

#     def total_images(self, obj):
#         return obj.images.count()

#     total_images.short_description = "Количество изображений"


# @admin.register(ProductImage)
# class ProductImageAdmin(admin.ModelAdmin):
#     list_display = ("preview", "product", "product_author")
#     list_filter = ("product__model", "product__author")
#     search_fields = ("product__product_name", "product__author__username")
#     readonly_fields = ("preview_front", "preview_back")

#     def preview(self, obj):
#         if obj.image_front:
#             return format_html(
#                 '<img src="{}" style="max-width:100px; max-height:100px;" />',
#                 obj.image_front.url,
#             )
#         return "Нет изображения"

#     preview.short_description = "Предпросмотр"

#     def product_author(self, obj):
#         return obj.product.author.username

#     product_author.short_description = "Автор"

#     def preview_front(self, obj):
#         if obj.image_front:
#             return format_html(
#                 '<img src="{}" style="max-width:300px; max-height:300px;" />',
#                 obj.image_front.url,
#             )
#         return "Нет изображения"

#     preview_front.short_description = "Изображение спереди"

#     def preview_back(self, obj):
#         if obj.image_back:
#             return format_html(
#                 '<img src="{}" style="max-width:300px; max-height:300px;" />',
#                 obj.image_back.url,
#             )
#         return "Нет изображения"


#     preview_back.short_description = "Изображение сзади"
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_name", "author", "price", "quantity", "qr_code")
    list_filter = ("author", "model__category", "model")
    search_fields = ("product_name", "description", "author__username")

    # если нужно отобразить миниатюру QR-кода
    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" style="max-width:100px; max-height:100px;" />',
                obj.qr_code.url,
            )
        return "Нет изображения"

    qr_code_preview.short_description = "QR-код"
 