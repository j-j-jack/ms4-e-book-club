from django.db import models
from django.db.models.fields import TextField
from products.models import Product, Category


class BookOfMonth(models.Model):
    class Meta:
        verbose_name_plural = "Book of Month"

    category = models.OneToOneField(
        Category, null=True, blank=True, on_delete=models.CASCADE, related_name="book_of_month")
    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)
    # there can only be one book for each book of the month instance
    book = models.OneToOneField(
        Product, null=True, blank=True, on_delete=models.SET_NULL, related_name="book_of_month_information")
    description = TextField(blank=True, null=True, max_length=2000)
    price = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name
