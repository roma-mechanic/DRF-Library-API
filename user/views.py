from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import UserProfile, User
from user.serializers import (
    UserSerializer,
    UserDetailSerializer,
    UserProfileListSerializer,
    UserProfileCreateSerializer,
    UserProfileDetailSerializer,
    UserListSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """create/register user"""

    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    """Detail info by user, update users info, delete user"""

    serializer_class = UserDetailSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UsersListView(generics.ListAPIView):
    """All users list"""

    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = (IsAdminUser,)


class APILogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if self.request.data.get("all"):
            token: OutstandingToken
            for token in OutstandingToken.objects.filter(user=request.user):
                _, _ = BlacklistedToken.objects.get_or_create(token=token)
            return Response(
                {"status": "OK, goodbye, all refresh tokens blacklisted"}
            )
        refresh_token = self.request.data.get("refresh_token")
        token = RefreshToken(token=refresh_token)
        token.blacklist()
        return Response({"status": "OK, goodbye"})


# class UserPostListAPIView(ListAPIView):
#     """Search for all borrows by a given user by his UserProfile ID"""
#
#     serializer_class = PostListSerializer
#
#     def get_queryset(self):
#         return (
#             Post.objects.filter(author__id=self.kwargs["pk"])
#             .select_related("author")
#             .prefetch_related("comments", "likes")
#         )


class UserProfileListView(generics.ListAPIView):
    queryset = UserProfile.objects.select_related("user")

    serializer_class = UserProfileListSerializer
    permission_classes = (IsAuthenticated | IsAdminUser,)

    def get_queryset(self):
        user = self.request.query_params.get("user")
        username = self.request.query_params.get("username")

        queryset = self.queryset

        if user:
            queryset = queryset.filter(user__email__icontains=user)

        if username:
            queryset = queryset.filter(username__icontains=username)
        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="user",
                type=str,
                description="Search user by email (ex. ?user=user@test.com)",
            ),
            OpenApiParameter(
                name="username",
                type=str,
                description="Search user by username  (ex: ?username=Bob)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class UserProfileCreateView(generics.CreateAPIView):
    queryset = UserProfile.objects.select_related("user")
    serializer_class = UserProfileCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserProfileDetailView(generics.RetrieveAPIView):
    queryset = UserProfile.objects.select_related("user")
    serializer_class = UserProfileDetailSerializer
    permission_classes = (IsAuthenticated | IsAdminUser,)


class UserProfileUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.select_related("user")
    serializer_class = UserProfileDetailSerializer
    permission_classes = (IsAuthenticated | IsAdminUser,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
