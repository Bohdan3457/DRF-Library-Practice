from django.db import transaction
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from payments.models import Payment


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        queryset = Borrowing.objects.all()

        if not user.is_staff:
            queryset = queryset.filter(user=user)
        else:
            user_id = self.request.query_params.get("user_id")
            if user_id:
                queryset = queryset.filter(user_id=user_id)

        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            if is_active.lower() == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active.lower() == "false":
                queryset = queryset.filter(actual_return_date__isnull=False)

        return queryset.select_related("book", "user")

    @action(detail=True, methods=["post"], url_path="return")
    def return_book(self, request, pk=None):
        borrowing = self.get_object()

        if borrowing.actual_return_date is not None:
            return Response(
                {"error": "This borrowing has already been returned."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():

            borrowing.actual_return_date = timezone.now().date()
            borrowing.save()

            book = borrowing.book
            book.inventory += 1
            book.save()

            serializer = self.get_serializer(borrowing)
            if (
                borrowing.actual_return_date
                > borrowing.expected_return_date
            ):
                days_overdue = (
                    borrowing.actual_return_date
                    - borrowing.expected_return_date
                ).days
                fine_multiplier = 2
                fine_amount = (
                    days_overdue
                    * borrowing.book.daily_fee
                    * fine_multiplier
                )
                Payment.objects.create(
                    status=Payment.StatusChoices.PENDING,
                    type=Payment.TypeChoices.FINE,
                    borrowing=borrowing,
                    money_to_pay=fine_amount,
                )
            return Response(serializer.data, status=status.HTTP_200_OK)
