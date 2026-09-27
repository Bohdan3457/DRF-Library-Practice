from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment

User = get_user_model()


class PaymentApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com", password="password123"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            cover="HARD",
            inventory=2,
            daily_fee=1.00,
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date="2026-10-01",
            expected_return_date="2026-10-05",
        )
        self.payment = Payment.objects.create(
            borrowing=self.borrowing,
            session_url="https://stripe.com/test",
            session_id="session_test_123",
            money_to_pay=10.00,
            status=Payment.StatusChoices.PENDING,
            payment_type=Payment.TypeChoices.PAYMENT,
        )
        self.payments_url = reverse("payments:payment-list")

    def test_auth_required_for_payments(self):
        response = self.client.get(self.payments_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_payments(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.payments_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
