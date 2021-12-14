from django.db import models

# Create your models here.
from django.db import models
from django.db.models.fields import CharField
from products.models import Product
from django.contrib.auth.models import User


class Review(models.Model):
    # use product.review_set to find reviews for product
    product = models.ForeignKey(Product, null=True, on_delete=models.CASCADE)
    # use user.review_set to find if user wrote review for specific product
    review_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    title = CharField(max_length=100, null=False, blank=False)
    review_body = models.TextField(null=False, blank=False)
    rating = models.IntegerField(null=False, blank=False, default=5)
    # likes = models.IntegerField(null=True, blank=False, default=0)
    # unlikes = models.IntegerField(null=True, blank=False, default=0)

    def __str__(self):
        return self.title
