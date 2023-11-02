from django.urls import path, include


from rest_framework import routers

from book.views import (
    BookReadOnlyViewSet,
    BookCreateView,
    BookUpdateDeleteView,
)

app_name = "book"

router = routers.SimpleRouter()
router.register(r"list", BookReadOnlyViewSet, basename="books-list")

urlpatterns = [
    path("", include(router.urls)),
    path("create/", BookCreateView.as_view(), name="book-create"),
    path(
        "<int:pk>/update/", BookUpdateDeleteView.as_view(), name="book-update"
    ),
]
