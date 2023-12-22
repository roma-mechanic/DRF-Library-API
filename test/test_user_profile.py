from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from test.sample_functions import sample_user_profile_object, sample_user
from user.models import UserProfile
from user.serializers import (
    UserProfileListSerializer,
    UserProfileDetailSerializer,
)


class UnauthenticatedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()

    def test_unauthenticated_user_cannot_create_profile(self):
        profile_data = {"user": self.user, "username": "test userrname"}
        url = reverse("user:userprofile-create")
        res = self.client.post(url, profile_data)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_get_profile_list(self):
        sample_user_profile_object()
        url = reverse("user:userprofile-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_get_profile_detail(self):
        user_profile = sample_user_profile_object()
        url = reverse("user:userprofile-detail", args=[user_profile.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_update_profile(self):
        profile = sample_user_profile_object()

        url = reverse("user:userprofile-update", args=[profile.id])
        update_data = {"username": "new username"}
        res = self.client.patch(url, update_data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_delete_profile(self):
        profile = sample_user_profile_object()

        url = reverse("user:userprofile-update", args=[profile.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserProfileAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()

        self.client.force_authenticate(self.user)
        # self.another_user = get_user_model().objects.create_user(
        #     email="another@user.com", password="anotherpass"
        # )

    def test_authenticated_user_can_create_profile(self):
        data = {"user": self.user, "username": "test userrname"}
        url = reverse("user:userprofile-create")
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_authenticated_user_can_get_profile_list(self):
        sample_user_profile_object()
        url = reverse("user:userprofile-list")
        res = self.client.get(url)
        profiles = UserProfile.objects.all()
        serializer = UserProfileListSerializer(profiles, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data["results"])

    def test_authenticated_user_can_get_profile_detail(self):
        profile = sample_user_profile_object()
        url = reverse("user:userprofile-detail", args=[profile.id])
        res = self.client.get(url)
        profiles = UserProfile.objects.get(user=self.user)
        serializer = UserProfileDetailSerializer(profiles)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    def test_authenticated_user_can_update_profile(self):
        profile = sample_user_profile_object()
        url = reverse("user:userprofile-update", args=[profile.id])
        update_data = {"username": "new username"}
        res = self.client.patch(url, update_data)
        profiles = UserProfile.objects.get(user=self.user)
        serializer = UserProfileDetailSerializer(profiles)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    def test_authenticated_user_can_delete_profile(self):
        profile = sample_user_profile_object()
        url = reverse("user:userprofile-update", args=[profile.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
