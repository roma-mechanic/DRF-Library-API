from django.db import models

from book.models import Book
from user.models import UserProfile


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField(auto_now_add=True)
    actual_return_date = models.DateField(auto_now_add=True)
    book = models.ManyToManyField(Book, related_name="borrowing")
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="borrowing")

    class Meta:
        ordering = ("-borrow_date",)

