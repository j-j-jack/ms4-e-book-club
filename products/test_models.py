from django.test import TestCase
from .models import Product


class TestModels(TestCase):

    def test_on_sale_defaults_to_true(self):
        test_book = Product.objects.create(
            name='test_book', author="test_author", price=2.50, description="test")
        print(test_book.currently_on_sale)
        self.assertTrue(test_book.currently_on_sale)

    def test_book_of_month_defaults_to_false(self):
        test_book = Product.objects.create(
            name='test_book', author="test_author", price=2.50, description="test")
        print(test_book.currently_on_sale)
        self.assertFalse(test_book.book_of_month)
