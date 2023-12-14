from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from borrowing.models import Borrowing
from borrowing.serializers import BorrowingSerializer
from test.test_book_api import sample_book
from user.models import UserProfile


def sample_borrowing(**params):
    user = get_user_model().objects.create_user(
        email="testuser@testuser.com", password="testpass"
    )
    test_user_profile = UserProfile.objects.create(
        user=user, username="testuser"
    )
    test_book_object = sample_book()

    defaults = {
        "borrow_date": "2023-12-27",
        "user": test_user_profile,
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


class AuthenticatedBorrowingAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@testuser.com", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)

    def sample_borrowing(self, **params):
        test_user_profile = UserProfile.objects.create(
            user=self.user, username="testuser"
        )
        test_book_object = sample_book()

        defaults = {
            "borrow_date": "2024-07-07",
            "user": test_user_profile,
            "is_active": True,
        }
        defaults.update(params)
        borrowing = Borrowing.objects.create(**defaults)
        borrowing.book.set([test_book_object])
        return borrowing

    def test_authenticated_user_can_access_list_borrowings(self):
        url = reverse("borrowing:borrowing-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_can_access_retrieve_borrowings(self):
        borrowing = self.sample_borrowing()
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
        id = response.data.get("id")
        if id:
            borrowing = Borrowing.objects.get(id=id)
            for key in borrowing_data:
                self.assertEqual(getattr(borrowing, key), borrowing_data[key])

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_authenticated_user_can_delete_borrowing(self):
        borrowing = self.sample_borrowing()
        url = reverse("borrowing:borrowing-detail", args=[borrowing.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Borrowing.objects.filter(id=borrowing.id).exists())
