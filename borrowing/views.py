from datetime import date

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingBookReturnSerializer,
)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("user").prefetch_related(
        "book"
    )
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

            return queryset.distinct()

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
        if self.action == "return_book":
            return BorrowingBookReturnSerializer
        return BorrowingSerializer

    @action(
        methods=["PATCH"],
        detail=True,
        url_path="return",
        permission_classes=[IsAdminUser],
    )
    def return_book(self, request, pk=None):
        borrowing = self.get_object()
        data = {"actual_return_date": date.today(), "is_active": False}
        serializer = self.get_serializer(borrowing, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
