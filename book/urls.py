from django.urls import path, include
from rest_framework import routers

from book.views import (
    BookReadOnlyViewSet,
)

app_name = "book"

router = routers.DefaultRouter()
router.register(r"", BookReadOnlyViewSet, basename="books-list")

urlpatterns = [path("", include(router.urls), name="books")]
