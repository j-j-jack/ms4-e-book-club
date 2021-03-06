from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.shortcuts import get_object_or_404
from stripe.api_resources import subscription

from .models import Order, OrderLineItemProduct, OrderLineItemSubscription
from products.models import Product
from profiles.models import UserProfile
from book_clubs.models import BookOfMonth
from profiles.models import UserProfile
import stripe
import json
import time
import datetime
import decimal


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order):
        """Send the user a confirmation email"""
        cust_email = order.email
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation-email-subject.txt',
            {'order': order})
        body = render_to_string(
            'checkout/confirmation_emails/confirmation-email-body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email]
        )

    def _send_invoice_paid_email(self, profile, email, paid):
        """Send the user a confirmation email for the monthly subscription payment"""
        cust_email = email
        user_clubs = profile.book_club_subscriptions_this_month.all()
        # provided in the stripe invoice
        amount_paid = paid
        subject = render_to_string(
            'checkout/confirmation_emails/sub-paid-confirmation-subject.txt',
            {'profile': profile})
        body = render_to_string(
            'checkout/confirmation_emails/sub-paid-confirmation-body.txt',
            {'profile': profile, 'amount_paid': amount_paid, 'user_clubs': user_clubs, 'date': datetime.datetime.now(), 'contact_email': settings.DEFAULT_FROM_EMAIL})

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email]
        )

    def _send_invoice_failed_email(self, profile, email):
        """Send the user a confirmation email for the monthly subscription payment"""
        cust_email = email

        subject = render_to_string(
            'checkout/confirmation_emails/sub-failed-subject.txt',
            {'profile': profile})
        body = render_to_string(
            'checkout/confirmation_emails/sub-failed-body.txt',
            {'profile': profile, 'date': datetime.datetime.now(), 'contact_email': settings.DEFAULT_FROM_EMAIL})

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email]
        )

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        intent = event.data.object
        user_profile = get_object_or_404(
            UserProfile, id=intent.metadata.user_profile)
        # necessary to calculate the price for line items if the order is not successfully
        # created in the checkout app
        subscription_count_before_order = user_profile.book_club_subscriptions_this_month.all().count()
        pid = intent.id
        bag = intent.metadata.bag
        for item_id, item_data in json.loads(bag).items():
            if item_data == 'S':
                # add the subscriptoins to current and next month if purchases
                user_profile.book_club_subscriptions_this_month.add(
                    int(item_id))
                user_profile.book_club_subscriptions_next_month.add(
                    int(item_id))
                user_profile.save()
                book = get_object_or_404(BookOfMonth, id=int(item_id)).book
                user_profile.owned_books.add(book.id)
                user_profile.save()
            elif item_data == 'P':
                # add any books purchased to the user profile
                book = get_object_or_404(Product, id=int(item_id))
                user_profile.owned_books.add(book.id)
                user_profile.save()
        # using the metadata to determine if the user wants their info saved
        save_info = intent.metadata.save_info
        billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping
        grand_total = round(intent.charges.data[0].amount / 100, 2)
        customer = intent.customer
        payment_method = intent.payment_method
        # this is necessary to ensure that payments continue in the future
        stripe.Customer.modify(
            customer,
            invoice_settings={
                "default_payment_method": payment_method},
        )
        # Clean data in the shipping details
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        # Update profile information if save_info was checked
        profile = None
        username = intent.metadata.username
        profile = UserProfile.objects.get(user__username=username)
        if save_info:
            profile.default_phone_number = shipping_details.phone
            profile.default_country = shipping_details.address.country
            profile.default_postcode = shipping_details.address.postal_code
            profile.default_town_or_city = shipping_details.address.city
            profile.default_street_address1 = shipping_details.address.line1
            profile.default_street_address2 = shipping_details.address.line2
            profile.default_county = shipping_details.address.state
            profile.save()

        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                # check if the order is already created
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        if order_exists:
            # send the confirmation email if the order exists
            self._send_confirmation_email(order)
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                status=200)
        else:
            # otherwise perform the same logic from the checkout app here and create a new order
            # before sending the confirmation email
            order = None
            try:
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                order.save()
                order_exists = True
                subscriptions_purchased = 0
                for item_id, item_data in json.loads(bag).items():
                    if item_data == 'P':
                        product = Product.objects.get(id=item_id)
                        order_line_item = OrderLineItemProduct(
                            order=order,
                            product=product,
                            lineitem_total=decimal.Decimal(2.50),
                        )
                        order_line_item.save()
                    elif item_data == 'S':
                        subscriptions_purchased += 1
                        total_subscriptions = subscriptions_purchased + subscription_count_before_order
                        if total_subscriptions < 3:
                            price = decimal.Decimal(2)
                        if total_subscriptions >= 3 and total_subscriptions < 5:
                            price = decimal.Decimal(1.75)
                        elif total_subscriptions >= 5:
                            price = decimal.Decimal(1.50)
                        book_of_month = BookOfMonth.objects.get(id=item_id)
                        order_subscription_line_item = OrderLineItemProduct(
                            order=order,
                            book_of_month=book_of_month,
                            lineitem_total=decimal.Decimal(price),
                        )
                        order_subscription_line_item.save()
                if order_exists:
                    self._send_confirmation_email(order)

            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {bag}{event["type"]} | ERROR: {e}', status=500)
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
            status=200)

    def handle_payment_intent_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)

    def handle_invoice_payment_succeeded(self, event):
        """
        Handle the payment of an invoice for a subscription
        """
        invoice = event.data.object
        customer = invoice.get('customer')
        profile = get_object_or_404(
            UserProfile, stripe_customer_id=customer)
        amount_paid = 0
        customer = stripe.Customer.retrieve(customer)
        customer_email = customer.get('email')
        if invoice.amount_paid > 0:

            profile.first_month = False
            user_resubscriptions = profile.book_club_subscriptions_next_month.all()
            profile.book_club_subscriptions_this_month.clear()
            # update the book club subscriptions from this month to the next month
            for club in user_resubscriptions:
                profile.book_club_subscriptions_this_month.add(club)
            user_clubs = profile.book_club_subscriptions_this_month.all()
            book_clubs = BookOfMonth.objects.all()
            for club in book_clubs:
                if club in user_clubs:
                    profile.owned_books.add(club.book)
            # only remove first month if the subscription is past the dummy price
            profile.save()
        else:
            amount_paid = 0
            subscription_count = 0
            user_clubs = profile.book_club_subscriptions_this_month.all()
            for club in user_clubs:
                subscription_count = subscription_count + 1
                if subscription_count < 2:
                    amount_paid = amount_paid + 2
                elif subscription_count >= 2 and subscription_count < 4:
                    amount_paid = amount_paid + 1.75
                else:
                    amount_paid = amount_paid + 1.50

        self._send_invoice_paid_email(
            profile, customer_email, amount_paid)
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)

    def handle_invoice_payment_failed(self, event):
        """
        Handle the failed payment of an invoice for a subscription
        """
        invoice = event.data.object
        customer = invoice.get('customer')
        profile = get_object_or_404(UserProfile, stripe_customer_id=customer)
        profile.book_club_subscriptions_next_month.clear()
        profile.book_club_subscriptions_this_month.clear()
        customer = stripe.Customer.retrieve(customer)
        customer_email = customer.get('email')
        subscription = invoice.get('subscription')
        # delete the customers subscription and profile on stripe
        stripe.Subscription.delete(subscription)
        stripe.Customer.delete(customer)
        # send the user an email to notify them that the payment failed and they are no longer subscribed
        self._send_invoice_failed_email(
            profile, customer_email)
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
