from django.db import models
from django.db.models.fields.json import JSONField


class Category(models.Model):
    class Meta:
        verbose_name_plural = "Categories"

    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)
    books = JSONField(null=True, blank=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name


class WiderCategory(models.Model):

    class Meta:
        verbose_name_plural = "Wider Categories"

    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)
    books = JSONField(null=True, blank=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name


class Product(models.Model):
    category = models.ForeignKey(
        'Category', null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=254)
    author = models.CharField(max_length=254)
    description = models.TextField(null=True, blank=True)
    book_of_month = models.BooleanField(blank=True, default=False)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True)
    reviews = models.JSONField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    sales_count = models.IntegerField(null=True, blank=True)
    currently_on_sale = models.BooleanField(blank=True, default=True)
    pdf = models.FileField(blank=True, null=True, upload_to="pdfs")

    def __str__(self):
        return self.name
