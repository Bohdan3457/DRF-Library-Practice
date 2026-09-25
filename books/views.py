from rest_framework.permissions import BasePermission, SAFE_METHODS
from books.serializers import BookSerializer
from rest_framework import viewsets
from books.models import Book


class IsAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view) -> bool:
        return bool(
            request.method in SAFE_METHODS or
            (request.user and request.user.is_staff)
        )


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrReadOnly,)
