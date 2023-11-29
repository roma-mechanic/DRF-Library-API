import os
import uuid

from django.db import models
from django.utils.text import slugify


def movie_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/post", filename)


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "hard"
        SOFT = "soft"

    title = models.CharField(
        max_length=100,
    )
    author = models.CharField(max_length=100)
    annotation = models.TextField(blank=True)
    cover = models.CharField(max_length=4, choices=CoverChoices.choices)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(null=True, upload_to=movie_image_file_path)

    class Meta:
        indexes = [models.Index(fields=["title", "author"])]

    def __str__(self):
        return f"{self.author}: {self.title},  daily fee {self.daily_fee} USD"
