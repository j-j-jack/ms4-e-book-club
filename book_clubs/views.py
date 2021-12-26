from time import time
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib import messages
import json
from products.models import Category, WiderCategory
from .models import BookOfMonth
from .forms import BookOfMonthForm
from profiles.models import UserProfile
import stripe
from django.conf import settings
from checkout.views import get_next_month_timestamp
# Create your views here.


def fiction_book_clubs(request):
    template = 'book_clubs/fiction-book-clubs.html'
    categories = Category.objects.all().filter(wider_category=1)
    list_of_category_ids = []
    for category in categories:
        list_of_category_ids.append(category.id)
    book_clubs = BookOfMonth.objects.all().filter(
        category__in=list_of_category_ids).order_by("category")
    subscriptions_in_bag = []
    if "bag" in request.session:
        print('in cookies')
        for item in request.session['bag']:
            if request.session['bag'].get(item) == 'S':
                subscriptions_in_bag.append(int(item))
    user_profile = get_object_or_404(UserProfile, user=request.user)
    book_club_subscriptions_this_month = user_profile.book_club_subscriptions_this_month.all()
    print(book_club_subscriptions_this_month)
    book_club_subscriptions_next_month = user_profile.book_club_subscriptions_next_month.all()
    print(book_club_subscriptions_this_month)
    context = {
        "book_clubs": book_clubs,
        "subscriptions_in_bag": subscriptions_in_bag,
        "book_club_subscriptions_this_month": book_club_subscriptions_this_month,
        "book_club_subscriptions_next_month": book_club_subscriptions_next_month,
    }
    return render(request, template, context)


def non_fiction_book_clubs(request):
    template = 'book_clubs/non-fiction-book-clubs.html'
    categories = Category.objects.all().filter(wider_category=2)
    list_of_category_ids = []
    for category in categories:
        list_of_category_ids.append(category.id)
    book_clubs = BookOfMonth.objects.all().filter(
        category__in=list_of_category_ids).order_by("category")
    subscriptions_in_bag = []
    if "bag" in request.session:
        print('in cookies')
        for item in request.session['bag']:
            if request.session['bag'].get(item) == 'S':
                subscriptions_in_bag.append(int(item))
    user_profile = get_object_or_404(UserProfile, user=request.user)
    book_club_subscriptions_this_month = user_profile.book_club_subscriptions_this_month.all()
    print(book_club_subscriptions_this_month)
    book_club_subscriptions_next_month = user_profile.book_club_subscriptions_next_month.all()
    print(book_club_subscriptions_this_month)
    context = {
        "book_clubs": book_clubs,
        "subscriptions_in_bag": subscriptions_in_bag,
        "book_club_subscriptions_this_month": book_club_subscriptions_this_month,
        "book_club_subscriptions_next_month": book_club_subscriptions_next_month,
    }
    return render(request, template, context)


def child_teen_book_clubs(request):
    template = 'book_clubs/child-teen-book-clubs.html'
    categories = Category.objects.all().filter(wider_category=3)
    list_of_category_ids = []
    for category in categories:
        list_of_category_ids.append(category.id)
    book_clubs = BookOfMonth.objects.all().filter(
        category__in=list_of_category_ids).order_by("category")
    subscriptions_in_bag = []
    if "bag" in request.session:
        print('in cookies')
        for item in request.session['bag']:
            if request.session['bag'].get(item) == 'S':
                subscriptions_in_bag.append(int(item))
    user_profile = get_object_or_404(UserProfile, user=request.user)
    book_club_subscriptions_this_month = user_profile.book_club_subscriptions_this_month.all()
    print(book_club_subscriptions_this_month)
    book_club_subscriptions_next_month = user_profile.book_club_subscriptions_next_month.all()
    print(book_club_subscriptions_this_month)
    context = {
        "book_clubs": book_clubs,
        "subscriptions_in_bag": subscriptions_in_bag,
        "book_club_subscriptions_this_month": book_club_subscriptions_this_month,
        "book_club_subscriptions_next_month": book_club_subscriptions_next_month,
    }
    return render(request, template, context)


@login_required
def edit_book_clubs(request):
    """ Edit the book clubs """

    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))
    categories = Category.objects.all()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    category_count = categories.count()
    if is_ajax:
        response = {'finished': False, }
        category = int(request.POST['category'])
        book_of_month_instance = get_object_or_404(
            BookOfMonth, category=category)
        form = BookOfMonthForm(
            category, request.POST, instance=book_of_month_instance)
        if form.is_valid():
            form.save()
        else:
            messages.error(
                request, 'Failed to  update book clubs. Please ensure the form is valid.')
        if category == category_count:
            response = {'finished': True, }
            messages.success(request, 'Successfully updated book clubs!')

        return HttpResponse(json.dumps(response), status=200)

    forms = []
    for cat in categories:
        forms.append(BookOfMonthForm(category=cat.id, auto_id=False))

    template = 'book_clubs/edit-book-clubs.html'
    context = {
        'forms': forms,
        'category_count': category_count,
    }

    return render(request, template, context)


@login_required
def unsubscribe_next_month(request, item_id):
    """Unsubscribe from a particular book club next month"""

    book_club = BookOfMonth.objects.get(pk=item_id)
    redirect_url = request.POST.get('redirect_url')
    user_profile = get_object_or_404(UserProfile, user=request.user)
    user_profile.book_club_subscriptions_next_month.remove(book_club)
    subscription_count = user_profile.book_club_subscriptions_next_month.all().count()
    stripe.api_key = settings.STRIPE_SECRET_KEY
    timestamp = get_next_month_timestamp()
    if user_profile.first_month:
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
        stripe.SubscriptionSchedule.modify(
            subscription.schedule,
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
                         'quantity': subscription_count},
                    ],
                    'start_date': subscription_schedule_phase_one_start_date,
                    'end_date': subscription_schedule_phase_one_end_date
                },
            ],
        )
    else:
        stripe.Subscription.modify(user_profile.stripe_subscription_id,
                                   quantity=subscription_count,)
    messages.success(
        request, f'You will not be subscribed to the {book_club.friendly_name} book club next month')
    return redirect(redirect_url)


@ login_required
def resubscribe_next_month(request, item_id):
    """Unsubscribe from a particular book club next month"""

    book_club = BookOfMonth.objects.get(pk=item_id)
    redirect_url = request.POST.get('redirect_url')
    user_profile = get_object_or_404(UserProfile, user=request.user)
    user_profile.book_club_subscriptions_next_month.add(book_club)
    subscription_count = user_profile.book_club_subscriptions_next_month.all().count()
    stripe.api_key = settings.STRIPE_SECRET_KEY
    timestamp = get_next_month_timestamp()
    if user_profile.first_month:
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
        stripe.SubscriptionSchedule.modify(
            subscription.schedule,
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
                         'quantity': subscription_count},
                    ],
                    'start_date': subscription_schedule_phase_one_start_date,
                    'end_date': subscription_schedule_phase_one_end_date
                },
            ],
        )
    else:
        stripe.Subscription.modify(user_profile.stripe_subscription_id,
                                   quantity=subscription_count,)
    messages.success(
        request, f'You are resubscribed to the {book_club.friendly_name} next month')
    return redirect(redirect_url)
