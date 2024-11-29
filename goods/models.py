# goods/models.py
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Category(models.Model):
    category_name = models.CharField(max_length=100,unique=True, verbose_name='Категория')
    category_icon =models.CharField(max_length=100, verbose_name='иконка', default='fas fa-box')

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):

        return self.category_name


class PhoneModel(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='phone_models')
    phone_name = models.CharField(max_length=100,unique=True, verbose_name='Модель телефона')

    class Meta:
        verbose_name = "Модель телефона"
        verbose_name_plural = "Модели телефона"

    def __str__(self):
        
        return self.phone_name


class ProductModel(models.Model):
    category = models.ForeignKey(PhoneModel, on_delete=models.CASCADE, related_name='models')
    model_name = models.CharField(max_length=100,unique=True, verbose_name='Называние модель')

    class Meta:
        verbose_name = "Называние модель"
        verbose_name_plural = "Называние модели"

    def __str__(self):
        return self.model_name

from io import BytesIO
from django.core.files import File
import qrcode


# goods/models.py
class Product(models.Model):
    product_name = models.CharField(max_length=100)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    custom_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Индивидуальная скидка")
    quantity = models.PositiveIntegerField()
    model = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    product_url = models.URLField(
        blank=True, null=True, verbose_name="URL страницы товара"
    )
    qr_code = models.ImageField(upload_to="qr_codes/", null=True, blank=True)

    class Meta:
        unique_together = ("product_name", "author")
        indexes = [
            models.Index(fields=["product_name", "author"]),
        ]  # Уникальность по названию и автору
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return f"{self.product_name} by {self.author.username}"

    def save(self, *args, **kwargs):
        # Генерация QR-кода при сохранении продукта
        if not self.qr_code and self.product_url and self.product_url.strip():
            try:
                print("Генерация QR-кода началась")

                # Настройка QR-кода
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(self.product_url)
                qr.make(fit=True)

                # Создание изображения QR-кода
                img = qr.make_image(fill_color="black", back_color="white").get_image()
                buffer = BytesIO()
                img.save(buffer, format="PNG")

                # Сохранение изображения QR-кода в поле модели
                buffer.seek(0)
                self.qr_code.save(f"{self.product_name}.png", File(buffer), save=False)
                print(f"QR-код сохранен: {self.qr_code.name}")

            except Exception as e:
                print(f"Ошибка при генерации QR-кода: {e}")

        # Сохранение объекта модели
        super().save(*args, **kwargs)


def user_directory_path(instance, filename):
    # Функция возвращает путь для загрузки файлов, уникальный для каждого пользователя
    return f"user_{instance.product.author.id}/{filename}"


class ProductImage(models.Model):
    product = models.ForeignKey(
        "Product", related_name="images", on_delete=models.CASCADE
    )
    image_front = models.ImageField(
        upload_to=user_directory_path, blank=True, null=True
    )

    class Meta:
        verbose_name = "Изображение продукта"
        verbose_name_plural = "Изображения продуктов"

    def __str__(self):
        return f"Изображение у {self.product.product_name} by {self.product.author.username}"
