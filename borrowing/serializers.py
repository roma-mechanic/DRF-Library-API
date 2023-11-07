from rest_framework import serializers

from book.serializers import BookSerializer, BookListSerializer
from borrowing.models import Borrowing
from user.serializers import (
    UserProfileDetailSerializer,
    UserProfileListSerializer,
)


class BorrowingSerializer(serializers.ModelSerializer):
    book = serializers.SlugRelatedField(
        slug_field="title", many=True, read_only=True
    )

    # book = BookListSerializer(many=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "is_active",
            "user",
        ]
        read_only_fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "user",
        ]


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "book",
        ]
