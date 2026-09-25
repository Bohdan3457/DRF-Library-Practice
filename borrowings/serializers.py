from django.db import transaction
from rest_framework import serializers
from borrowings.models import Borrowing
from payments.models import Payment
from payments.services import create_stripe_session
from borrowings.telegram_services import send_telegram_notification


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        )
        read_only_fields = ("user",)

    def validate(self, attrs):
        book = attrs.get("book", None)
        borrow_date = attrs.get("borrow_date", None)
        expected_return_date = attrs.get("expected_return_date", None)
        if book and book.inventory <= 0:
            raise serializers.ValidationError("sorry, but inventory == 0")

        if (borrow_date and expected_return_date and
                borrow_date > expected_return_date):
            raise serializers.ValidationError("Error")

        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            book = validated_data.get("book")
            user = self.context["request"].user
            validated_data["user"] = user
            book.inventory -= 1
            book.save()
            borrowing = Borrowing.objects.create(**validated_data)

            session_url, session_id, money_to_pay = (
                create_stripe_session(borrowing)
            )

            Payment.objects.create(
                status=Payment.StatusChoices.PENDING,
                payment_type=Payment.TypeChoices.PAYMENT,
                borrowing=borrowing,
                session_url=session_url,
                session_id=session_id,
                money_to_pay=money_to_pay,
            )

            message = (
                f"New borrowing created!\n"
                f"Book: {borrowing.book}\n"
                f"User: {borrowing.user}\n"
                f"Expected return date: {borrowing.expected_return_date}"
            )
            send_telegram_notification(message)
            return borrowing
