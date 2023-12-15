from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from book.models import Book
from book.serializers import BookListSerializer
from borrowing.models import Borrowing
from borrowing.serializers import BorrowingSerializer, BorrowingBookReturnSerializer
from test.test_book_api import sample_book
from user.models import UserProfile


def sample_user(**params):
    defaults = {"email": "sample@sample.com", "password": "samplepassword"}
    defaults.update(params)
    user, created = get_user_model().objects.get_or_create(
        email=defaults["email"], defaults=defaults
    )
    if not created:
        user.set_password(defaults["password"])
        user.save()
    return user


def sample_user_profile_object(**params):
    defaults = {
        "user": sample_user(),
        "username": "sample_username",
        # "telebot_chat_ID": 1111111111
    }
    defaults.update(params)
    user_profile, created = UserProfile.objects.get_or_create(
        user=defaults["user"], defaults=defaults
    )
    return user_profile


def sample_borrowing(**params):
    test_book_object = sample_book()

    defaults = {
        "borrow_date": "2023-12-27",
        "user": sample_user_profile_object(),
        "is_active": True,
    }
    defaults.update(params)
    borrowing = Borrowing.objects.create(**defaults)
    borrowing.book.set([test_book_object])
    return borrowing


class UnauthenticatedTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_user_cannot_access_list_borrowings(self):
        url = reverse("borrowing:borrowing-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_access_retrieve_borrowings(self):
        borrowing = sample_borrowing()

        url = reverse("borrowing:borrowing-detail", args=[borrowing.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_create_borrowings(self):
        url = reverse("borrowing:borrowing-list")
        data = {
            "borrow_date": "2024-02-16",
            "book": "Test book",
            "user": "testuser",
            "is_active": True,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_edit_borrowings(self):
        borrowing = sample_borrowing()
        url = reverse("borrowing:borrowing-detail", args=[borrowing.id])
        data = {
            "borrow_date": "2024-12-28",
            "book": "Updated book",
            "user": "testuser",
            "is_active": True,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@testuser.com", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)

    def test_authenticated_user_can_access_list_borrowings(self):
        url = reverse("borrowing:borrowing-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_can_access_retrieve_borrowings(self):
        book = sample_book()
        user_profile = sample_user_profile_object(
            user=self.user, username="sampleusername"
        )
        borrowing = sample_borrowing(user=user_profile)
        borrowing.book.add(book)
        borrowing.save()
        serializer = BorrowingSerializer(borrowing)
        url = reverse("borrowing:borrowing-detail", args=[borrowing.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)

    def test_authenticated_user_can_create_borrowings(self):
        url = reverse("borrowing:borrowing-list")
        test_book_object = sample_book()
        borrowing_data = {
            "borrow_date": "2024-04-17",
            "book": test_book_object,
            "user": self.user,
            "is_active": True,
        }
        response = self.client.post(url, borrowing_data)
        bor_id = response.data.get("id")
        if bor_id:
            borrowing = Borrowing.objects.get(id=bor_id)

            for key in borrowing_data:
                self.assertEqual(getattr(borrowing, key), borrowing_data[key])

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_the_number_of_books_after_borrowing_is_decreasing(self):
        book = sample_book()

        user_profile = sample_user_profile_object(
            user=self.user, username="sampleusername"
        )

        borrowing_data = {
            "borrow_date": "2024-04-17",
            "book": book.id,
            "user": user_profile,
        }
        url = reverse("borrowing:borrowing-list")
        response = self.client.post(url, borrowing_data)

        final_book_count = Book.objects.get(id=book.id).inventory

        url = reverse("book:books-detail", args=[book.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(final_book_count, book.inventory - 1)




    def test_authenticated_user_can_delete_borrowing(self):
        book = sample_book()
        user_profile = sample_user_profile_object(
            user=self.user, username="sampleusername"
        )
        borrowing = sample_borrowing(user=user_profile)
        borrowing.book.add(book)
        borrowing.save()
        url = reverse("borrowing:borrowing-detail", args=[borrowing.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Borrowing.objects.filter(id=borrowing.id).exists())


class AdminBorrowingTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user(
            email="admin@admin.com",
            password="adminpassword",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_admin_can_filter_all_borrowing(self):
        user1 = sample_user(
            email="user_1@user_1.com", password="user1password"
        )
        user2 = sample_user(
            email="user_2@user_2.com", password="user2password"
        )
        user_profile1 = sample_user_profile_object(
            user=user1, username="user_1"
        )
        user_profile2 = sample_user_profile_object(
            user=user2, username="user_2"
        )
        borrowing1 = sample_borrowing(user=user_profile1)
        borrowing2 = sample_borrowing(user=user_profile2, is_active=False)
        serializer1 = BorrowingSerializer(borrowing1)
        serializer2 = BorrowingSerializer(borrowing2)

        url = reverse("borrowing:borrowing-list")

        response = self.client.get(url, data={"user_id": user_profile1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

        response = self.client.get(
            url, data={"is_active": borrowing2.is_active}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer1.data, response.data)

    def test_the_number_of_books_after_return_is_increased(self):
        borrowing = sample_borrowing()
        serializer = BorrowingSerializer(borrowing)
        print(f"Sample borrowing is created\n{serializer.data}")

        url = reverse("borrowing:borrowing-return-book", args=(borrowing.id,))
        print(url)
        response = self.client.patch(url)
        # response = self.client.patch(f"http://127.0.0.1:8000/api/borrowings/{borrowing.id}/return/")
        print(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        final_book_count = borrowing.book.all()
        for book in final_book_count:
            print(f"book_inventory  {book.inventory}")
        print(final_book_count)
        serializer = BookListSerializer(final_book_count, many=True)
        print(serializer.data)
