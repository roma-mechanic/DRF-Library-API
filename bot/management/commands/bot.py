from django.core.management.base import BaseCommand

from bot.main_bot import bot


class Command(BaseCommand):
    help = "Telegram-bot"

    def handle(self, *args, **options):
        bot.polling()
