from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly

from book.models import Book
from book.serializers import BookSerializer, BookListSerializer


class BookViewSet(viewsets.ModelViewSet):
    """
    Lists all the books . Anon users can read books list.

    EXAMPLE:

        GET -> /books/ -> create book and returns all books.
        GET -> /books/{id}/ -> return the book detail, update, delete books.
        Only admin can create, update, delete books.
    """

    queryset = Book.objects.all()
    # permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        return BookSerializer

    def get_permissions(self):
        if self.action == "list":
            self.permission_classes = (permissions.AllowAny,)
        if self.action == "retrieve":
            self.permission_classes = (IsAuthenticated,)
        if self.action in ("update", "destroy", "create", "partial_update"):
            self.permission_classes = (IsAdminUser,)
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        title = self.request.query_params.get("title")
        author = self.request.query_params.get("author")

        queryset = self.queryset

        if title:
            queryset = queryset.filter(title__icontains=title)

        if author:
            queryset = queryset.filter(author__icontains=author)
        return queryset.distinct()

    @extend_schema(
        summary="Search books by title or author",
        parameters=[
            OpenApiParameter(
                name="title",
                type=str,
                description="Filter by title (ex. ?title=Harry)",
            ),
            OpenApiParameter(
                name="author",
                type=str,
                description="Filter by authors username  (ex: ?author=Bob)",
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
