from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import UserProfile
from book_clubs.models import BookOfMonth
from .forms import UserProfileForm

from checkout.models import Order


@login_required
def profile(request):
    """ Display the user's profile. """
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(
                request, 'Update failed, please ensure the form is valid')
    else:
        form = UserProfileForm(instance=profile)
    orders = profile.orders.all()
    book_clubs = BookOfMonth.objects.all()
    template = 'profiles/profile.html'
    user_profile = get_object_or_404(UserProfile, user=request.user)
    user_profile
    book_of_the_month = get_object_or_404(BookOfMonth, pk=2)
    print(book_of_the_month)
    user_profile.book_club_subscriptions_this_month.add(book_of_the_month)
    book_club_subscriptions_this_month = user_profile.book_club_subscriptions_this_month.all()
    print(book_club_subscriptions_this_month)
    subscriptions_in_bag = []
    if request.session['bag']:
        for item in request.session['bag']:
            if request.session['bag'].get(item) == 'S':
                subscriptions_in_bag.append(int(item))
    context = {
        'form': form,
        'orders': orders,
        'on_profile_page': True,
        'user_profile': user_profile,
        'book_club_subscriptions_this_month': book_club_subscriptions_this_month,
        'book_clubs': book_clubs,
        'subscriptions_in_bag': subscriptions_in_bag,
    }

    return render(request, template, context)


def order_history(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    messages.info(request, (
        f'This is a past confirmation for order number {order_number}. '
        'A confirmation email was sent on the order date.'
    ))

    template = 'checkout/checkout-success.html'
    context = {
        'order': order,
        'from_profile': True,
    }

    return render(request, template, context)
