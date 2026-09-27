from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book

User = get_user_model()


class BookApiTests(APITestCase):
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
            inventory=5,
            daily_fee=2.00,
        )
        self.books_url = reverse("books:book-list")

    def test_list_books(self):
        response = self.client.get(self.books_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_book_requires_admin(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "New Book",
            "author": "New Author",
            "cover": "SOFT",
            "inventory": 3,
            "daily_fee": 1.50,
        }
        response = self.client.post(self.books_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.books_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
