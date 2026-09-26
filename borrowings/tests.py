from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment

User = get_user_model()


class BorrowingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com", password="password123"
        )
        self.admin_user = User.objects.create_superuser(
            email="admin@test.com", password="password123"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=2,
            daily_fee=10.00,
        )
        self.borrowings_url = reverse("borrowings:borrowing-list")

    def test_auth_required_for_borrowings(self):
        response = self.client.get(self.borrowings_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_borrowing_decreases_inventory(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "book": self.book.id,
            "borrow_date": "2026-10-01",
            "expected_return_date": "2026-10-05",
        }
        response = self.client.post(self.borrowings_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 1)

    def test_return_borrowing_increases_inventory(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date="2026-10-01",
            expected_return_date="2026-10-05",
        )
        self.book.inventory = 1
        self.book.save()

        self.client.force_authenticate(user=self.user)
        return_url = reverse(
            "borrowings:borrowing-return-book", args=[borrowing.id])

        response = self.client.post(return_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 2)

        borrowing.refresh_from_db()
        self.assertIsNotNone(borrowing.actual_return_date)

    def test_cannot_return_book_with_pending_payment(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date="2026-10-01",
            expected_return_date="2026-10-05",
        )
        Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            payment_type=Payment.TypeChoices.PAYMENT,
            borrowing=borrowing,
            money_to_pay=50.00,
            session_url="https://stripe.com/test",
            session_id="test_session_id_1",
        )

        self.client.force_authenticate(user=self.user)
        return_url = reverse(
            "borrowings:borrowing-return-book", args=[borrowing.id])

        response = self.client.post(return_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_cannot_return_already_returned_book(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date="2026-10-01",
            expected_return_date="2026-10-05",
            actual_return_date=date.today(),
        )

        self.client.force_authenticate(user=self.user)
        return_url = reverse(
            "borrowings:borrowing-return-book", args=[borrowing.id])

        response = self.client.post(return_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("borrowings.views.create_stripe_session")
    def test_overdue_return_creates_fine_and_stripe_session(
        self, mock_create_stripe
    ):
        past_expected_date = date.today() - timedelta(days=3)
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=past_expected_date - timedelta(days=5),
            expected_return_date=past_expected_date,
        )
        self.book.inventory = 1
        self.book.save()

        self.client.force_authenticate(user=self.user)
        return_url = reverse(
            "borrowings:borrowing-return-book", args=[borrowing.id])

        response = self.client.post(return_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        fine_payment = Payment.objects.filter(
            borrowing=borrowing, payment_type=Payment.TypeChoices.FINE
        ).first()

        self.assertIsNotNone(fine_payment)
        self.assertEqual(fine_payment.status, Payment.StatusChoices.PENDING)
        mock_create_stripe.assert_called_once()
