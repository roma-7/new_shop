from django.core.management.base import BaseCommand

from notification.bot import SimpleTelegramBot


class Command(BaseCommand):
    help = "Runs Telegram Bot"

    def handle(self, *args, **options):
        bot = SimpleTelegramBot()
        bot.run()
