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
    # the three lines below track which actions the user can complete in the subscriptions section
    # they can add a subscription they have not subscribed to to their bag
    # they can unsubscribe and resubscribe to current subscriptions
    book_club_subscriptions_this_month = user_profile.book_club_subscriptions_this_month.all()
    book_club_subscriptions_next_month = user_profile.book_club_subscriptions_next_month.all()
    subscriptions_in_bag = []
    if 'bag' in request.session:
        for item in request.session['bag']:
            if request.session['bag'].get(item) == 'S':
                subscriptions_in_bag.append(int(item))
    context = {
        'form': form,
        'orders': orders,
        'on_profile_page': True,
        'user_profile': user_profile,
        'book_club_subscriptions_this_month': book_club_subscriptions_this_month,
        'book_club_subscriptions_next_month': book_club_subscriptions_next_month,
        'book_clubs': book_clubs,
        'subscriptions_in_bag': subscriptions_in_bag,
    }

    return render(request, template, context)


def order_history(request, order_number):
    """
    view to display orders made by the customer previously when clicked on from the profile page
    """

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
