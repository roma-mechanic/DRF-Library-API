from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, generics
from rest_framework.permissions import AllowAny, IsAdminUser

from book.models import Book
from book.serializers import BookSerializer, BookListSerializer


class BookReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lists all the books . Anon users can read books list.

    EXAMPLE:
        GET -> /books/list/ -> returns all books
        GET -> /books/list/{id}/ -> return the book detail
    """

    queryset = Book.objects.all()
    serializer_class = BookListSerializer
    permission_classes = (AllowAny,)

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
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class BookCreateView(generics.CreateAPIView):
    """
    Create  new book. AdminUser only.

    EXAMPLE:
        POST -> /books/create/-> create new book
    """

    serializer_class = BookSerializer
    permission_classes = (IsAdminUser,)


class BookUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """Only admin can change or delete books
    PUT, PATCH, DELETE -> /books/<id>/update/ -> put,
    patch, delete book with books ID
    """

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminUser,)
