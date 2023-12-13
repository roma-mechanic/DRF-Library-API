from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from book.models import Book
from book.serializers import BookListSerializer, BookSerializer


def sample_book(**params):
    defaults = {
        "title": "Sample Book",
        "author": "Test Author",
        "cover": "hard",
        "inventory": 10,
        "daily_fee": 1.0,
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


class UnauthenticatedBookAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_user_can_access_list_books(self):
        sample_book()
        sample_book()
        sample_book()

        books = Book.objects.all()
        serializer = BookListSerializer(books, many=True)

        response = self.client.get(reverse("book:books-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(len(response.data), 3)

    def test_unauthenticated_user_cannot_access_retrieve_books(self):
        book = sample_book()
        response = self.client.get(
            reverse("book:books-detail", args=[book.id])
        )
        print(reverse("book:books-detail", args=[book.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBookAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@testuser.com", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)

    def test_authenticated_user_can_access_books(self):
        response = self.client.get(reverse("book:books-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_cannot_created_books(self):
        book_data = {
            "title": "New Book",
            "author": "New Author",
            "cover": "soft",
            "inventory": 5,
            "daily_fee": 0.99,
        }
        response = self.client.post(reverse("book:books-list"), book_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_cannot_edit_books(self):
        book = sample_book()
        response = self.client.put(
            reverse("book:books-detail", args=[book.id]),
            {"title": "Updated Book", "author": "Updated Author"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_cannot_delete_books(self):
        book = sample_book()

        response = self.client.delete(
            reverse("book:books-detail", args=[book.id])
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_books(self):
        book1 = sample_book(title="New Book", author="New Author")
        book2 = sample_book(title="Another Book", author="Another Author")
        serializer1 = BookListSerializer(book1)
        serializer2 = BookListSerializer(book2)
        response = self.client.get(
            reverse("book:books-list"), {"title": "New Book"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

        response = self.client.get(
            reverse("book:books-list"), {"author": "Another Author"}
        )
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer1.data, response.data)


class AdminBookAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.com",
            password="testpassword",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_admin_user_can_create_books(self):
        book_data = {
            "title": "New Book",
            "author": "New Author",
            "cover": "soft",
            "inventory": 5,
            "daily_fee": Decimal("0.99"),
        }

        response = self.client.post(reverse("book:books-list"), book_data)
        book = Book.objects.get(id=response.data["id"])
        for key in book_data:
            self.assertEqual(getattr(book, key), book_data[key])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_user_can_edit_books(self):
        book = sample_book()
        book_data = {"title": "Updated Book", "author": "Updated Author"}
        response = self.client.patch(
            reverse("book:books-detail", args=[book.id]),
            book_data,
        )
        book.refresh_from_db()
        for key in book_data:
            self.assertEqual(getattr(book, key), book_data[key])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_can_delete_books(self):
        book = sample_book()
        response = self.client.delete(
            reverse("book:books-detail", args=[book.id])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
