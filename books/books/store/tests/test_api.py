import json

from django.contrib.auth.models import User
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from django.urls import reverse
from rest_framework import status

from ..models import Book, UserBookRelation
from ..serializers import BooksSerializer


class BooksAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.book_1 = Book.objects.create(name='Test book 1', price=35, author_name='Author 1', owner=self.user)
        self.book_2 = Book.objects.create(name='Test book 2', price=25, author_name='Author 2')
        self.book_3 = Book.objects.create(name='Test book 2', price=25, author_name='Author 3, Test book 1')

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
            "author_name": self.book_1.author_name,
            "owner": self.book_1.owner.id,
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
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update_owner(self):
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

    def test_update_not_owner(self):
        self.user_2 = User.objects.create(username='test_username_2')
        url = reverse('book-detail', args=(self.book_1.id, ))
        data = {
                "name": self.book_1.name,
                "price": "45.00",
                "author_name": self.book_1.author_name
             }

        json_data = json.dumps(data)
        self.client.force_login(self.user_2)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.book_1.refresh_from_db()
        self.assertEqual(response.data, {'detail': ErrorDetail(string='You do not have permission to perform this action.', code='permission_denied')})
        self.assertEqual(35, self.book_1.price)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_update_not_owner_but_staff(self):
        self.user_2 = User.objects.create(username='test_username_2', is_staff=True)
        url = reverse('book-detail', args=(self.book_1.id, ))
        data = {
                "name": self.book_1.name,
                "price": "45.00",
                "author_name": self.book_1.author_name
             }

        json_data = json.dumps(data)
        self.client.force_login(self.user_2)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.book_1.refresh_from_db()
        self.assertEqual(45, self.book_1.price)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_delete_owner(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-detail', args=(self.book_1.id, ))
        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(2, Book.objects.all().count())

    def test_delete_not_owner(self):
        self.user_2 = User.objects.create(username='test_username_2')
        self.assertEqual(3, Book.objects.all().count())

        url = reverse('book-detail', args=(self.book_1.id, ))
        self.client.force_login(self.user_2)
        response = self.client.delete(url)
        self.assertEqual(response.data, {'detail': ErrorDetail(string='You do not have permission to perform this action.', code='permission_denied')})
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(3, Book.objects.all().count())

    def test_delete_not_owner_but_staff(self):
        self.user_2 = User.objects.create(username='test_username_2', is_staff=True)
        self.assertEqual(3, Book.objects.all().count())

        url = reverse('book-detail', args=(self.book_1.id, ))
        self.client.force_login(self.user_2)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(2, Book.objects.all().count())


class UserBookRelationTestCase(APITestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username='test_username_1')
        self.user_2 = User.objects.create(username='test_username_2')

        self.book_1 = Book.objects.create(name='Test book 1', price=35, author_name='Author 1', owner=self.user_1)
        self.book_2 = Book.objects.create(name='Test book 2', price=25, author_name='Author 2')

    def test_like_and_in_bookmarks_and_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id, ))
        data = {
                "like": True,
             }
        json_data = json.dumps(data)
        self.client.force_login(self.user_1)

        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        relation = UserBookRelation.objects.get(user=self.user_1, book=self.book_1)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(relation.like)

        data = {
                "in_bookmarks": True,
             }
        json_data = json.dumps(data)

        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        relation = UserBookRelation.objects.get(user=self.user_1, book=self.book_1)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(relation.in_bookmarks)

        data = {
                "rate": 5,
             }
        json_data = json.dumps(data)

        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        relation = UserBookRelation.objects.get(user=self.user_1, book=self.book_1)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(relation.rate, 5)

    def test_rate_wrong(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id, ))
        data = {
                "rate": 6,
             }
        json_data = json.dumps(data)
        self.client.force_login(self.user_1)

        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        relation = UserBookRelation.objects.get(user=self.user_1, book=self.book_1)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)
        self.assertEqual(relation.rate, None)
