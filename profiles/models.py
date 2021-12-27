from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import BooleanField
from django.db.models.signals import post_save
from django.dispatch import receiver
from book_clubs.models import BookOfMonth
from django_countries.fields import CountryField
from products.models import Product


class UserProfile(models.Model):
    """
    A user profile model for maintaining default
    billing information and order history
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)
    book_club_subscriptions_this_month = models.ManyToManyField(
        BookOfMonth, related_name='users_subscribed_this_month', null=True, blank=True)
    book_club_subscriptions_next_month = models.ManyToManyField(
        BookOfMonth, related_name="users_subscribed_next_month", null=True, blank=True)
    default_phone_number = models.CharField(
        max_length=20, null=True, blank=True)
    default_country = CountryField(
        blank_label='Country *', null=True, blank=True)
    default_postcode = models.CharField(max_length=20, null=True, blank=True)
    default_town_or_city = models.CharField(
        max_length=40, null=True, blank=True)
    default_street_address1 = models.CharField(
        max_length=80, null=True, blank=True)
    default_street_address2 = models.CharField(
        max_length=80, null=True, blank=True)
    default_county = models.CharField(max_length=80, null=True, blank=True)
    # fields used for tracking the user on stripe
    stripe_customer_id = models.CharField(
        max_length=300, null=True, blank=True)
    stripe_subscription_id = models.CharField(
        max_length=300, null=True, blank=True)

    owned_books = models.ManyToManyField(
        Product, null=True, blank=True, related_name='owned_by')
    # field used to update schedule depending whether the user is in their first month
    # this is necessary as the user is inititally subscribed to a  dummy price which costs 0 to
    # ensure a subscription id is created for handling the webhooks from stripe
    first_month = BooleanField(default=False)
    subscriptions_in_bag = models.PositiveIntegerField(
        null=False, blank=False, default=0)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update the user profile
    """
    if created:
        UserProfile.objects.create(user=instance)
    # Existing users: just save the profile
    instance.userprofile.save()
