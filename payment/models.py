from django.db import models

from borrowing.models import Borrowing


class Payment(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "pending"  # очікування
        PAID = "paid"  # оплачено

    class TypeChoices(models.TextChoices):
        PAYMENT = "payment"
        FINE = "fine"

    status = models.CharField(
        max_length=7,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )
    type = models.CharField(
        max_length=7, choices=TypeChoices.choices, default=TypeChoices.PAYMENT
    )
    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, related_name="payment"
    )
    session_url = models.URLField(max_length=500)
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(decimal_places=2, max_digits=5)
