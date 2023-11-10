from rest_framework import serializers

from book.serializers import BookSerializer
from borrowing.models import Borrowing


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
        ]
        read_only_fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "is_active",
            "user",
        ]

    # def create(self, validated_data):
    #     print(validated_data)
    #     books_data = validated_data.pop("book")
    #     print(books_data, validated_data)
    #
    #     borrow = Borrowing.objects.create(**validated_data)
    #
    #     for book in books_data:
    #         if book.inventory != 0:
    #             book.inventory -= 1
    #             book.save()
    #             borrow.book.add(book)
    #         else:
    #             raise serializers.ValidationError(
    #                 f"The book '{book.title}' temporarily unavailable"
    #             )
    #     return borrow


class BorrowingCreateSerializer(serializers.ModelSerializer):
    # book = BookSerializer(many=True)

    class Meta:
        model = Borrowing
        fields = [
            "book",
        ]

    def create(self, validated_data):
        print(validated_data)
        books_data = validated_data.pop("book")
        print(books_data, validated_data)

        borrow = Borrowing.objects.create(**validated_data)

        for book in books_data:
            if book.inventory != 0:
                book.inventory -= 1
                book.save()
                borrow.book.add(book)
                borrow.save()
            else:
                raise serializers.ValidationError(
                    f"The book '{book.title}' temporarily unavailable"
                )
        return borrow
