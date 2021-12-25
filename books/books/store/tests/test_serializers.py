from unittest import TestCase

from ..models import Book
from ..serializers import BooksSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        book_1 = Book.objects.create(name='Test book 1', price=35)
        book_2 = Book.objects.create(name='Test book 2', price=25)
        data = BooksSerializer([book_1, book_2], many=True).data
        expected_data = [
            {
                "id": book_1.id,
                "name": "Test book 1",
                "price": "35.00"
             },
            {
                "id": book_2.id,
                "name": "Test book 2",
                "price": "25.00"
            }
        ]
        self.assertEqual(expected_data, data)