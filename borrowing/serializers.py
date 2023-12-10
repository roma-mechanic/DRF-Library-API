from django.db import transaction
from rest_framework import serializers

from DRF_Library_API import settings
from borrowing.models import Borrowing
from payment.models import Payment
from payment.views import (
    create_checkout_session,
)


class BorrowingSerializer(serializers.ModelSerializer):
    book_title = serializers.SlugRelatedField(
        source="book", slug_field="title", many=True, read_only=True
    )
    book_inventory = serializers.SlugRelatedField(
        source="book",
        slug_field="inventory",
        many=True,
        read_only=True,
    )
    payment_status = serializers.SlugRelatedField(
        source="payment", slug_field="status", read_only=True, many=True
    )

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "book_title",
            "book_inventory",
            "is_active",
            "user",
            "total_cost",
            "payment_status",
        ]
        read_only_fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "is_active",
            "user",
        ]

    def create(self, validated_data):
        with transaction.atomic():
            books_data = validated_data.pop("book")
            print(books_data)
            borrow = Borrowing.objects.create(**validated_data)
            for book in books_data:
                if book.inventory != 0:
                    book.inventory -= 1
                    book.save()
                    borrow.book.add(book)

                else:
                    raise serializers.ValidationError(
                        f"The book '{book.title}' temporarily unavailable"
                    )
            create_checkout_session(
                borrow.id,
                self.context["request"],
                days=settings.BORROWING_DAYS,
                payment_type=Payment.TypeChoices.PAYMENT,
                payment_status=Payment.StatusChoices.PENDING,
            )

        return borrow


class BorrowingBookReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ["actual_return_date", "is_active"]
