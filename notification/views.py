# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import TelegramUserProfile
import telegram
from django.conf import settings
from django.http import JsonResponse


@login_required
def connect_telegram(request):
    if request.method == "POST":
        chat_id = request.POST.get("chat_id")

        try:
            # Валидация chat_id
            if not chat_id:
                raise ValueError("Chat ID не может быть пустым")

            # Для групп chat_id должен быть отрицательным, для личных чатов - положительным
            chat_id = str(chat_id).strip()
            if not (chat_id.startswith("-") or chat_id.replace("-", "").isdigit()):
                raise ValueError("Неверный формат Chat ID")

            # Сохраняем или обновляем профиль
            profile, created = TelegramUserProfile.objects.get_or_create(
                user=request.user
            )
            profile.telegram_chat_id = chat_id
            profile.is_active = True
            profile.save()

            messages.success(request, "Чат успешно подключен!")
            return JsonResponse({"status": "success"})

        except ValueError as e:
            return JsonResponse({"status": "error", "message": str(e)})
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": "Ошибка при подключении чата"}
            )


    return render(request, "notification/telegram_bot.html")
