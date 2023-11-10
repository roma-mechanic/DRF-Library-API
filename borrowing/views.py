from django.shortcuts import render
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingCreateSerializer,
    # BorrowingCreateSerializer,
)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("user").prefetch_related(
        "book"
    )
    # serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_staff:
            user_id = self.request.query_params.get("user_id")

            if user_id:
                queryset = queryset.filter(user__id__in=user_id)

            is_active = self.request.query_params.get("is_active")
            if is_active:
                queryset = queryset.filter(is_active=is_active)

            return queryset

        return queryset.filter(user=self.request.user.profile)

    @extend_schema(
        summary="Search user borrowings by user ID or/and borrowings is_active True or False ",
        parameters=[
            OpenApiParameter(
                name="user_id",
                type={"type": "list", "items": {"type": "number"}},
                description="Search user by User_id (ex: ?user_id=2,3",
            ),
            OpenApiParameter(
                name="is_active",
                type=str,
                description="Search is_active borrowings (ex: ?is_active=True)",
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.profile)

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingSerializer
