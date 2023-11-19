import datetime
from datetime import date

from django.db import models
from django.db.models import Count, F, Sum

from DRF_Library_API.settings import BORROWING_DAYS
from book.models import Book
from user.models import UserProfile


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField(blank=True, null=True)
    actual_return_date = models.DateField(null=True, blank=True, default=None)
    book = models.ManyToManyField(Book, related_name="borrowing")
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="borrowing"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("-borrow_date",)
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["expected_return_date"]),
        ]

    def clean(self):
        self.expected_return_date = date.today() + datetime.timedelta(
            days=BORROWING_DAYS
        )

    def save(self, **kwargs):
        self.full_clean()
        return super().save(**kwargs)

    @property
    def total_cost(self):
        return self.book.aggregate(Sum("daily_fee")).values()
