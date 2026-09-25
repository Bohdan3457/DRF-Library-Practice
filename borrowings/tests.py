from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book
from borrowings.models import Borrowing

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
