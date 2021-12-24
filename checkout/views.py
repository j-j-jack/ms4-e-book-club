from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import Settings, settings
from django.contrib.auth.decorators import login_required
from stripe.api_resources.payment_intent import PaymentIntent

from book_clubs.models import BookOfMonth
from e_book_club.settings import STRIPE_SECRET_KEY
from .forms import OrderForm
from .models import Order, OrderLineItemProduct, OrderLineItemSubscription
from products.models import Product
from bag.contexts import bag_contents

from profiles.models import UserProfile
from profiles.forms import UserProfileForm

import stripe
import json
import time


@ login_required
@require_POST
def cache_checkout_data(request):
    try:
        user_profile = get_object_or_404(
            UserProfile, user=request.user)
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
            'user_profile': request.user.userprofile.id,
        })
        intent = stripe.PaymentIntent.retrieve(pid)
        customer = intent.customer
        stripe.PaymentIntent.modify(pid, customer=customer)
        stripe.Customer.modify(customer,
                               email=request.POST.get('email'),
                               name=request.POST.get('name'),)

        subscription_quantity = user_profile.book_club_subscriptions_this_month.all().count()
        for item in request.session.get('bag'):
            print(item, request.session.get('bag').get(item) + 'ch')
            if request.session.get('bag').get(item) == 'S':
                subscription_quantity += 1
        print('subscription quanity:', subscription_quantity)
        existing_subscription = None
        try:
            existing_subscription = user_profile.stripe_subscription_id
            print('existing subscription' + existing_subscription)
        except:
            print('broke here line 55')
        if existing_subscription != None or existing_subscription != '':
            try:
                stripe.Subscription.modify(existing_subscription,
                                           quantity=subscription_quantity,)
            except:
                print('broken here line 63')
        else:
            subscription = stripe.SubscriptionSchedule.create(
                customer=customer,
                start_date='now',
                end_behavior="release",
                phases=[
                    {
                        'items': [
                            {'price': settings.STRIPE_PRICE,
                             'quantity': subscription_quantity},
                        ],
                    },
                ],
            )
            user_profile.stripe_subscription_id = subscription.subscription
            user_profile.save()
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be \
            processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)


@ login_required
def checkout(request):
    bag = request.session['bag']
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    user_profile = get_object_or_404(
        UserProfile, user=request.user)
    if request.method == 'POST':
        bag = request.session.get('bag', {})
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            order.original_bag = json.dumps(bag)
            order.save()

            for item_id, item_data in bag.items():
                try:
                    if item_data == 'P':
                        product = Product.objects.get(id=item_id)
                        order_line_item = OrderLineItemProduct(
                            order=order,
                            product=product,
                        )
                        order_line_item.save()
                    elif item_data == 'S':
                        book_of_month = BookOfMonth.objects.get(id=item_id)
                        order_subscription_line_item = OrderLineItemSubscription(
                            order=order,
                            book_of_month=book_of_month,
                        )
                        order_subscription_line_item.save()

                except Product.DoesNotExist:
                    messages.error(request, (
                        "One of the products in your bag wasn't found in our database. "
                        "Please call us for assistance!")
                    )
                    order.delete()
                    return redirect(reverse('view_bag'))

            request.session['save_info'] = 'save-info' in request.POST
            return redirect(reverse('checkout_success', args=[order.order_number]))
        else:
            messages.error(request, 'There was an error with your form. \
                Please double check your information.')

    else:
        bag = request.session.get('bag', {})
        if not bag:
            messages.error(
                request, 'There\'s nothing in your bag at the moment')
            return redirect(reverse('products'))

        current_bag = bag_contents(request)
        total = current_bag['grand_total']
        stripe_total = round(total*100)
        stripe.api_key = stripe_secret_key
        existing_customer = user_profile.stripe_customer_id
        customer = None
        if existing_customer != None or existing_customer != '':
            customer = stripe.Customer.create(
                name=request.user
            )
            user_profile.stripe_customer_id = customer.id
            user_profile.save()
        else:
            customer = stripe.Customer.retrieve(existing_customer)
        intent = stripe.PaymentIntent.create(
            customer=customer.id,
            setup_future_usage='off_session',
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
            automatic_payment_methods={
                'enabled': True,
            },
        )
        # print(stripe.PaymentIntent.retrieve(intent.id))
        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                order_form = OrderForm(initial={
                    'full_name': profile.user.get_full_name(),
                    'email': profile.user.email,
                    'phone_number': profile.default_phone_number,
                    'country': profile.default_country,
                    'postcode': profile.default_postcode,
                    'town_or_city': profile.default_town_or_city,
                    'street_address1': profile.default_street_address1,
                    'street_address2': profile.default_street_address2,
                    'county': profile.default_county,
                })
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
        else:
            order_form = OrderForm()

        if not stripe_public_key:
            messages.warning(
                request, "Stripe public key is missing... Did you forget to set it in your environment variables?")
        template = 'checkout/checkout.html'
        context = {
            'order_form': order_form,
            'stripe_public_key': stripe_public_key,
            'client_secret': intent.client_secret,
        }

        return render(request, template, context)


def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """

    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)

    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        # Attach the user's profile to the order
        order.user_profile = profile
        order.save()

        # Save the user's info
        if save_info:
            profile_data = {
                'default_phone_number': order.phone_number,
                'default_country': order.country,
                'default_postcode': order.postcode,
                'default_town_or_city': order.town_or_city,
                'default_street_address1': order.street_address1,
                'default_street_address2': order.street_address2,
                'default_county': order.county,
            }
            user_profile_form = UserProfileForm(profile_data, instance=profile)
            if user_profile_form.is_valid():
                user_profile_form.save()

    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')

    if 'bag' in request.session:
        del request.session['bag']

    template = 'checkout/checkout-success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)
