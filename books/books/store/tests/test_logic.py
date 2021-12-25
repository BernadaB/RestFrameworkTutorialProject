from unittest import TestCase

from ..logic import operations


class LogicTestCase(TestCase):
    def test_plus(self):
        result = operations(5, 8, '+')
        self.assertEqual(result, 13)

    def test_minus(self):
        result = operations(5, 8, '-')
        self.assertEqual(result, -3)

    def test_multiply(self):
        result = operations(5, 8, '*')
        self.assertEqual(result, 40)