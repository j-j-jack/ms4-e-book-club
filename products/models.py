from django.db import models
from django.db.models.fields import BooleanField
from django.db.models.fields.json import JSONField
from django.db.models import Avg


class WiderCategory(models.Model):

    class Meta:
        verbose_name_plural = "Wider Categories"

    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

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
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True)
    book_of_month = BooleanField(null=True, blank=False, default=True)
    image = models.ImageField(null=True, blank=True)
    sales_count = models.IntegerField(null=True, blank=True)
    currently_on_sale = models.BooleanField(blank=True, default=True)
    pdf = models.FileField(blank=True, null=True, upload_to="pdfs")

    def __str__(self):
        return self.name

    def update_rating(self):
        """
        Update grand total each time a line item is added,
        accounting for delivery costs.
        """

        self.rating = self.reviews.aggregate(
            Avg('rating'))['rating__avg']
        self.save()
        print(self.rating)

    def get_name(self):
        return self.name


class Category(models.Model):
    class Meta:
        verbose_name_plural = "Categories"

    wider_category = models.ForeignKey(
        'WiderCategory', null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name
