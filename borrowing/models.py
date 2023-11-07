import datetime
from datetime import date

from django.db import models

from DRF_Library_API.settings import BORROWING_DAYS
from book.models import Book
from user.models import UserProfile


# def borrowings_day():
#     return datetime.date.today() + datetime.timedelta(days=BORROWING_DAYS)


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField(editable=False)
    actual_return_date = models.DateField(auto_now_add=True)
    book = models.ManyToManyField(Book, related_name="borrowing")
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="borrowing"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("-borrow_date",)

    def clean(self):
        self.expected_return_date = self.borrow_date + datetime.timedelta(
            days=BORROWING_DAYS
        )

    def save(self, **kwargs):
        self.clean()
        return super().save(**kwargs)
