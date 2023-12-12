from datetime import date

from celery import shared_task

from django.conf import settings

from borrowing.models import Borrowing
from borrowing.serializers import BorrowingSerializer
from bot.main_bot import telegram_bot_sendtext


@shared_task
def checking_borrowings_overdue():
    borrowings = (
        Borrowing.objects.filter(is_active=True)
        .filter(expected_return_date__lte=date.today())
        .select_related("user")
        .prefetch_related("book")
    )
    if borrowings:
        serializer = BorrowingSerializer(borrowings, many=True)
        message = f"Next borrowings are overdue {serializer.data}"
        telegram_bot_sendtext(message, settings.ADMIN_CHAT_ID)
    else:
        telegram_bot_sendtext(
            "No borrowings overdue today", settings.ADMIN_CHAT_ID
        )
