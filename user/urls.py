from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from user.views import (
    CreateUserView,
    ManageUserView,
    APILogoutView,
    UserProfileListView,
    UserProfileCreateView,
    UserProfileDetailView,
    UserProfileUpdateDeleteView,
)

app_name = "user"

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("logout/", APILogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("me/", ManageUserView.as_view(), name="manage"),
    # path("<int:pk>/posts/", UserPostListAPIView.as_view(), name="user-posts"),
    path(
        "user_profile/",
        UserProfileListView.as_view(),
        name="userprofile-list",
    ),
    path(
        "user_profile/create/",
        UserProfileCreateView.as_view(),
        name="userprofile-create",
    ),
    path(
        "user_profile/<int:pk>/",
        UserProfileDetailView.as_view(),
        name="userprofile-detail",
    ),
    path(
        "user_profile/<int:pk>/update/",
        UserProfileUpdateDeleteView.as_view(),
        name="userprofile-update",
    ),
]
