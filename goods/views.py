from decimal import Decimal
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Product, ProductImage, Category, PhoneModel, ProductModel
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404

from django.utils import timezone
from analytics.models import SalesRecord, StockHistory, DiscountRecord

from django.db.models import Sum, F
from datetime import timedelta
from .forms import *


@login_required
def create_product(request):
    if request.method == "POST":
        product_name = request.POST.get("product-name")
        description = request.POST.get("product-description")
        price = request.POST.get("product-price")
        cost_price = request.POST.get("product-cost-price")
        quantity = request.POST.get("product-quantity")
        category_id = request.POST.get("product-category")
        phone_model_id = request.POST.get("phone-model")
        model_id = request.POST.get("product-model")

        try:
            category = Category.objects.get(id=category_id)
            phone_model = PhoneModel.objects.get(id=phone_model_id, category=category)
            model = ProductModel.objects.get(id=model_id, category=phone_model)

            if Product.objects.filter(
                product_name=product_name, author=request.user
            ).exists():
                messages.error(
                    request,
                    "Продукт с таким названием уже существует для вашего профиля.",
                )
                return redirect("goods:create_product")

            product = Product.objects.create(
                product_name=product_name,
                model=model,
                author=request.user,
                description=description,
                price=price,
                cost_price=cost_price,
                quantity=quantity,
            )

            # Задаем URL страницы товара и сохраняем его
            product.product_url = request.build_absolute_uri(
                reverse("goods:product_detail", args=[product.id])
            )
            product.save()

            # Добавление изображений продукта, если они загружены
            front_image = request.FILES.get("product-image-front")
            if front_image:
                image = ProductImage.objects.create(product=product, image_front=front_image)
                print(f"Физический путь файла: {image.image_front.path}")
                print(f"URL файла: {image.image_front.url}")

            messages.success(request, "Продукт успешно создан.")
            return redirect("users:control-panel")

        except Category.DoesNotExist:
            messages.error(request, "Указанная категория не найдена.")
        except PhoneModel.DoesNotExist:
            messages.error(request, "Указанная модель телефона не найдена.")
        except ProductModel.DoesNotExist:
            messages.error(request, "Указанная модель продукта не найдена.")
        except Exception as e:
            messages.error(request, f"Произошла ошибка при создании продукта: {str(e)}")

        return redirect("goods:create_product")

    # Получение категорий для формы
    categories = Category.objects.all()
    phone_models = PhoneModel.objects.all()
    models = ProductModel.objects.all()
    return render(
        request,
        "goods/create_product.html",
        {"categories": categories, "phone_models": phone_models, "models": models},
    )


def error(request):
    return render(request, "goods/error.html")


def get_phone_models(request, category_id):
    phone_models = PhoneModel.objects.filter(category_id=category_id).values(
        "id", "phone_name"
    )
    return JsonResponse(list(phone_models), safe=False)


def get_product_models(request, category_id, phone_model_id):
    product_models = ProductModel.objects.filter(category_id=phone_model_id).values(
        "id", "model_name"
    )
    return JsonResponse(list(product_models), safe=False)


def categories_view(request):
    # Получаем период за последние 30 дней
    last_30_days = timezone.now() - timedelta(days=30)

    # Получаем популярные товары только текущего пользователя
    popular_products = (
        Product.objects.filter(
            sales_records__date__gte=last_30_days,
            author=request.user,
        )
        .annotate(
            total_sold=Sum("sales_records__quantity_sold"),
            total_revenue=Sum(
                F("sales_records__quantity_sold") * F("sales_records__sale_price")
            ),
        )
        .filter(total_sold__gt=0)
        .order_by("-total_sold")
        .select_related("model", "model__category", "model__category__category")
        .prefetch_related("images")[:5]
    )

    # Получаем все категории
    categories = Category.objects.all()

    context = {"categories": categories, "popular_products": popular_products}

    return render(request, "goods/categories.html", context)


def phone_models_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    phone_models = PhoneModel.objects.filter(category=category)
    return render(
        request,
        "goods/phone_models.html",
        {"category": category, "phone_models": phone_models},
    )


@login_required
def product_catalog(request, category_id=None, phone_model_id=None):
    # Базовый queryset для товаров текущего пользователя
    base_queryset = (
        Product.objects.select_related("model", "model__category")
        .prefetch_related("images")
        .filter(author=request.user)
    )

    # Получаем выбранную модель из формы
    selected_product_model = request.GET.get("product_model")

    # Поисковый запрос
    search_query = request.GET.get("search", "")
    if search_query:
        products = base_queryset.filter(
            Q(product_name__icontains=search_query)
            | Q(model__category__phone_name__icontains=search_query)
            | Q(model__model_name__icontains=search_query)
        )
    else:
        products = base_queryset

    # Фильтры по категории и модели телефона
    if category_id:
        products = products.filter(model__category__category_id=category_id)

    if phone_model_id:
        products = products.filter(model__category_id=phone_model_id)

    # Фильтр по конкретной модели (например, iPhone 11 Pro)
    if selected_product_model:
        products = products.filter(model_id=selected_product_model)

    # Получаем модели для конкретного телефона
    product_models = []
    if phone_model_id:
        product_models = ProductModel.objects.filter(
            category_id=phone_model_id, product__author=request.user
        ).distinct()

    # Сортировка
    products = products.order_by("-id")

    # Пагинация
    page = request.GET.get("page", 1)
    paginator = Paginator(products, 8)

    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)

    # Вычисляем диапазон страниц
    max_pages = paginator.num_pages
    current_page = int(page)

    if max_pages <= 5:
        page_range = range(1, max_pages + 1)
    else:
        if current_page <= 3:
            page_range = range(1, 6)
        elif current_page >= max_pages - 2:
            page_range = range(max_pages - 4, max_pages + 1)
        else:
            page_range = range(current_page - 2, current_page + 3)

    context = {
        "products": products_page,
        "page_range": page_range,
        "max_pages": max_pages,
        "current_page": current_page,
        "category_id": category_id,
        "phone_model_id": phone_model_id,
        "product_models": product_models,
        "search_query": search_query,
        "selected_model": selected_product_model,
    }

    return render(request, "goods/phone_catalog.html", context)


# goods/
def product_detail(request, product_id):
    product = get_object_or_404(
        Product.objects.select_related("model", "model__category").prefetch_related(
            "images"
        ),
        id=product_id,
    )

    context = {
        "product": product,
        "images": product.images.first(),
    }

    return render(request, "goods/product_detail.html", context)


# goods/views.py
@login_required
def sell_product(request, product_id):
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "message": "Метод не поддерживается"}, status=405
        )

    try:
        quantity = int(request.POST.get("quantity", 1))
        # Изменили имя поля на discount_value
        discount_value = Decimal(request.POST.get("discount_value", "0"))
        discount_type = request.POST.get("discount_type", "Фиксированная")

        if quantity <= 0:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Количество должно быть положительным числом",
                },
                status=400,
            )

        with transaction.atomic():
            product = get_object_or_404(Product, id=product_id, author=request.user)

            if product.quantity < quantity:
                return JsonResponse(
                    {
                        "success": False,
                        "message": f"Недостаточно товара. В наличии: {product.quantity}",
                    },
                    status=400,
                )

            # Преобразуем цену к Decimal
            sale_price = Decimal(str(product.price))  # Безопасное преобразование

            # Проверяем корректность скидки
            if discount_value < 0:
                return JsonResponse(
                    {"success": False, "message": "Скидка не может быть отрицательной"},
                    status=400,
                )

            if discount_type == "Процент":
                if discount_value > 100:
                    return JsonResponse(
                        {
                            "success": False,
                            "message": "Процент скидки не может быть больше 100",
                        },
                        status=400,
                    )
                discount_amount = sale_price * (discount_value / Decimal("100"))
            else:
                if discount_value > sale_price:
                    return JsonResponse(
                        {
                            "success": False,
                            "message": "Скидка не может быть больше цены товара",
                        },
                        status=400,
                    )
                discount_amount = discount_value

            # Рассчитываем финальную цену с учетом скидки
            final_price = sale_price - discount_amount

            # Уменьшаем количество товара
            product.quantity -= quantity
            product.save()

            # Создаем запись о продаже
            sales_record = SalesRecord.objects.create(
                product=product,
                quantity_sold=quantity,
                sale_price=final_price,
                category=product.model.category.category,
                date=timezone.now(),
            )

            # Создаем запись о скидке, если она есть
            if discount_amount > 0:
                DiscountRecord.objects.create(
                    sales_record=sales_record,
                    discount_type=discount_type,
                    discount_value=discount_amount,
                    date=timezone.now(),
                    product_name=product.product_name,
                    product_price=sale_price,  # Исходная цена
                    quantity_sold=quantity,
                    final_price=final_price,  # Цена после скидки
                )

            return JsonResponse(
                {
                    "success": True,
                    "message": "Товар успешно продан",
                    "remaining_quantity": product.quantity,
                }
            )

    except ValueError as ve:
        print(f"ValueError: {ve}")
        return JsonResponse(
            {"success": False, "message": "Неверный формат данных"}, status=400
        )
    except Exception as e:
        print(f"Ошибка: {e}")
        return JsonResponse(
            {"success": False, "message": "Произошла ошибка при продаже товара"},
            status=500,
        )


@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk, author=request.user)
    product_image = product.images.first() or None

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        image_form = ProductImageForm(
            request.POST, request.FILES, instance=product_image
        )

        if form.is_valid() and image_form.is_valid():
            with transaction.atomic():
                # Сохраняем основную информацию о товаре
                product = form.save(commit=False)
                product.author = request.user
                product.save()

                # Сохраняем изображение, если оно было загружено
                if image_form.cleaned_data.get("image_front"):
                    if product_image:
                        image_form.save()
                    else:
                        new_image = image_form.save(commit=False)
                        new_image.product = product
                        new_image.save()

            messages.success(request, "Товар успешно обновлен")
            return redirect("goods:categories")
    else:
        form = ProductForm(instance=product)
        image_form = ProductImageForm(instance=product_image)

    return render(
        request,
        "goods/edit_product.html",
        {"form": form, "image_form": image_form, "product": product},
    )


@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk, author=request.user)

    if request.method == "POST":
        product.delete()
        messages.success(request, "Товар успешно удален")
        return redirect("goods:categories")

    return render(request, "goods/confirm_delete.html", {"product": product})
