import json

from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from django.urls import reverse
from rest_framework import status

from ..models import Book
from ..serializers import BooksSerializer


class BooksAPITestCase(APITestCase):
    def setUp(self):
        self.book_1 = Book.objects.create(name='Test book 1', price=35, author_name='Author 1')
        self.book_2 = Book.objects.create(name='Test book 2', price=25, author_name='Author 2')
        self.book_3 = Book.objects.create(name='Test book 2', price=25, author_name='Author 3, Test book 1')
        self.user = User.objects.create(username='test_username')

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        serializer_data = BooksSerializer([self.book_1, self.book_2, self.book_3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_detail_get(self):
        url = reverse('book-detail', args=(self.book_1.id, ))
        response = self.client.get(url)
        expected_data = {
            "id": self.book_1.id,
            "name": self.book_1.name,
            "price": '35.00',
            "author_name": self.book_1.author_name
        }
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(expected_data, response.data)

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': 25})
        serializer_data = BooksSerializer([self.book_2, self.book_3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Test book 1'})
        serializer_data = BooksSerializer([self.book_1, self.book_3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-list')
        data = {
            "name": "Test book 1",
            "price": "35.00",
            "author_name": 'Author 1'
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Book.objects.all().count())

    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id, ))
        data = {
                "name": self.book_1.name,
                "price": "45.00",
                "author_name": self.book_1.author_name
             }

        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.book_1.refresh_from_db()
        self.assertEqual(45, self.book_1.price)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_delete(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-detail', args=(self.book_1.id, ))
        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(2, Book.objects.all().count())


