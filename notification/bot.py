import telebot
from django.conf import settings


class SimpleTelegramBot:
    def __init__(self):
        self.bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)
        self.setup_handlers()

    def setup_handlers(self):
        @self.bot.message_handler(commands=["start"])
        def start(message):
            """Приветствие при старте"""
            self.bot.reply_to(
                message,
                "Привет! Бот настроен и готов работать. "
                "Вам не нужно ничего делать - уведомления придут автоматически. 🚀",
            )

        @self.bot.message_handler(func=lambda message: True)
        def ignore_messages(message):
            """Игнорируем все остальные сообщения"""
            self.bot.reply_to(
                message,
                "Бот работает в автоматическом режиме. "
                "Никаких дополнительных действий не требуется.",
            )

    def run(self):  # Добавлен метод run
        self.bot.polling(none_stop=True)
