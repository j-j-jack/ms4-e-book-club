from django.db import models
from products.models import Product, Category


class BookOfMonth(models.Model):
    class Meta:
        verbose_name_plural = "Book of Month"

    category = models.OneToOneField(
        Category, null=True, blank=True, on_delete=models.CASCADE, related_name="book_of_month")
    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)
    book = models.OneToOneField(
        Product, null=True, blank=True, on_delete=models.SET_NULL, related_name="book_of_month_information")

    def __str__(self):
        return self.name
