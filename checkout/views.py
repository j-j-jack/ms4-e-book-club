from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required


from book_clubs.models import BookOfMonth
from .forms import OrderForm
from .models import Order, OrderLineItemProduct, OrderLineItemSubscription
from products.models import Product
from bag.contexts import bag_contents

from profiles.models import UserProfile
from profiles.forms import UserProfileForm
from django.db.models import Q
import decimal

import stripe
import json
import datetime


@login_required
@require_POST
def cache_checkout_data(request):
    """ view to gather the checkout data in order to modify the payment intent as necessary
    from the form on the page before it is submitted"""
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
        # it is necessary to compare the customer in the paymentIntent with the id in the userprofile
        # in the webhook handler
        stripe.PaymentIntent.modify(pid, customer=customer)
        stripe.Customer.modify(customer,
                               email=request.POST.get('email'),
                               name=request.POST.get('name'),)

        subscription_quantity = user_profile.book_club_subscriptions_this_month.all().count()
        subscription_in_bag = False
        for item in request.session.get('bag'):
            if request.session.get('bag').get(item) == 'S':
                subscription_quantity += 1
                subscription_in_bag = True
        if subscription_in_bag:
            # only create a new subscription if there is none currently
            existing_subscription = user_profile.stripe_subscription_id
            if existing_subscription == None or existing_subscription == '':
                # function used to calculate the 1st timestamp of next month as stripe requires
                timestamp = get_next_month_timestamp()
                subscription_schedule = stripe.SubscriptionSchedule.create(
                    customer=customer,
                    end_behavior='release',
                    start_date='now',
                    phases=[
                        {
                            'items': [
                                {'price': settings.STRIPE_DUMMY_PRICE, 'quantity': 1},
                            ],
                            'end_date': timestamp,
                        },
                        {
                            'items': [
                                {'price': settings.STRIPE_PRICE,
                                    'quantity': subscription_quantity},
                            ],
                        },
                    ],
                )

                user_profile.stripe_subscription_id = subscription_schedule.subscription
                user_profile.save()
            else:
                if user_profile.first_month:
                    # if still in the first month the schedule needs to be modified rather than
                    # the subscription.
                    subscription = stripe.Subscription.retrieve(
                        user_profile.stripe_subscription_id)
                    subscription_schedule = stripe.SubscriptionSchedule.retrieve(
                        subscription.schedule)
                    subscription_schedule_phase_zero_start_date = subscription_schedule.phases[
                        0].start_date
                    subscription_schedule_phase_zero_end_date = subscription_schedule.phases[
                        0].end_date
                    subscription_schedule_phase_one_start_date = subscription_schedule.phases[
                        1].start_date
                    subscription_schedule_phase_one_end_date = subscription_schedule.phases[
                        1].end_date
                    stripe.SubscriptionSchedule.modify(subscription.schedule,
                                                       phases=[
                                                           {
                                                               'items': [
                                                                   {'price': settings.STRIPE_DUMMY_PRICE,
                                                                    'quantity': 1},
                                                               ],
                                                               'start_date': subscription_schedule_phase_zero_start_date,
                                                               'end_date': subscription_schedule_phase_zero_end_date},
                                                           {
                                                               'items': [
                                                                   {'price': settings.STRIPE_PRICE,
                                                                    'quantity': subscription_quantity},
                                                               ],
                                                               'start_date': subscription_schedule_phase_one_start_date,
                                                               'end_date': subscription_schedule_phase_one_end_date
                                                           },
                                                       ],
                                                       )
                else:
                    stripe.Subscription.modify(existing_subscription,
                                               quantity=subscription_quantity,)
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be \
            processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)


@login_required
def checkout(request):
    bag = request.session['bag']
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    user_profile = get_object_or_404(
        UserProfile, user=request.user)
    if request.method == 'POST':
        bag = request.session.get('bag', {})
        # data which is put on the order instance
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
            subscriptions_purchased = 0
            current_subscription_count = user_profile.book_club_subscriptions_this_month.all().count()
            for item_id, item_data in bag.items():
                try:

                    price = decimal.Decimal(0)
                    if item_data == 'P':
                        product = Product.objects.get(id=item_id)
                        order_line_item = OrderLineItemProduct(
                            order=order,
                            product=product,
                            lineitem_total=2.50,
                        )
                        order_line_item.save()
                    elif item_data == 'S':
                        # subscription prices sent to the order line items are calculated based on
                        # the current subscriptions and the subscriptions in the bag.
                        subscriptions_purchased += 1
                        total_subscriptions = subscriptions_purchased + current_subscription_count
                        if total_subscriptions < 3:
                            price = decimal.Decimal(2)
                        if total_subscriptions >= 3 and total_subscriptions < 5:
                            price = decimal.Decimal(1.75)
                        elif total_subscriptions >= 5:
                            price = decimal.Decimal(1.50)
                        book_of_month = BookOfMonth.objects.get(id=item_id)
                        order_subscription_line_item = OrderLineItemSubscription(
                            order=order,
                            book_of_month=book_of_month,
                            lineitem_total=price,
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
        # create a new customer now as it needs to be accessed later and attached to the payment intent
        if existing_customer == None or existing_customer == '':
            customer = stripe.Customer.create(
                name=request.user
            )
            user_profile.first_month = True
            user_profile.stripe_customer_id = customer.id
            user_profile.save()
        else:
            customer = stripe.Customer.retrieve(existing_customer)

        intent = stripe.PaymentIntent.create(
            customer=customer.id,
            # this allows the payment method to be attached to the customer automatically
            # this is necessary for taking subscriptions when the user is not online to pay manually
            setup_future_usage='off_session',
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
            automatic_payment_methods={
                'enabled': True,
            },
        )
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
        # this list is used to show the prices on the template. It is not part of the order logic.
        subscription_prices = []
        if request.user.is_authenticated:
            user_profile = get_object_or_404(UserProfile, user=request.user)
            current_subscription_count = user_profile.book_club_subscriptions_this_month.all().count()
            subscriptions_in_bag = user_profile.subscriptions_in_bag
            total_subscriptions = current_subscription_count + subscriptions_in_bag
            for i in range(total_subscriptions+1):
                if i > current_subscription_count:
                    if i < 3:
                        subscription_prices.append(2)
                    elif i >= 3 and i < 5:
                        subscription_prices.append(1.75)
                    elif i >= 5:
                        subscription_prices.append(1.50)
            if 'bag' in request.session:
                bag = request.session['bag']
                position = 0
                for item in request.session['bag']:
                    if bag.get(item) == 'P':
                        subscription_prices.insert(position, 0)
                    position += 1
        template = 'checkout/checkout.html'
        context = {
            'order_form': order_form,
            'stripe_public_key': stripe_public_key,
            'client_secret': intent.client_secret,
            'subscription_prices': subscription_prices,
        }

        return render(request, template, context)


@login_required
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
            # saving the user form information provided for future usage and convenience
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


@login_required
def order_search(request):
    """
    view to return a search for orders
    """
    # prevent non store admins from using the order search
    if request.user.is_superuser:
        template = 'checkout/order-search.html'
        context = {}
        if request.GET:
            if 'q' in request.GET:
                query = request.GET['q']
                if not query:
                    messages.error(
                        request, "You didn't enter any search criteria!")
                    return redirect('order_search')
                orders = Order.objects.all()
                # search using the order number or customer name
                queries = Q(order_number__icontains=query) | Q(
                    full_name__icontains=query)
                orders = orders.filter(queries)
                if orders.count() == 0:
                    messages.info(
                        request, "Your query didn't return any results. Adjust your query and try again.")
                context = {
                    "orders": orders
                }

        return render(request, template, context)
    else:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))


def get_next_month_timestamp():
    """
    function used to provide the timestamp for the first day of next month to stripe
    """
    date = datetime.datetime.now()
    month = int(date.strftime("%m"))
    year = int(date.strftime("%y"))
    # end of a year logic
    if month == 12:
        month = 1
        year = year + 1
    else:
        month = month + 1
    year = int('20' + str(year))
    ts = datetime.datetime(year, month, 1)
    ts = int(ts.timestamp())
    return ts
