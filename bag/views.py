from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import (
    render, redirect, reverse, HttpResponse, get_object_or_404
)
from django.contrib import messages
from book_clubs.models import BookOfMonth

from products.models import Product
from profiles.models import UserProfile


def view_bag(request):
    """ A view to return the index page """
    # because the prices are not set in stone. they must be tracked manually as pages load
    subscription_prices = []
    if request.user.is_authenticated:
        user_profile = get_object_or_404(UserProfile, user=request.user)
        current_subscription_count = user_profile.book_club_subscriptions_this_month.all().count()
        subscriptions_in_bag = user_profile.subscriptions_in_bag
        total_subscriptions = current_subscription_count + subscriptions_in_bag
    # The prices are calculated by calculating the users current subscriptions
    # Then adding the price to the list manually
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
            # products are marked with 0 in the array to accomodate the for loop on the template page
            if bag.get(item) == 'P':
                subscription_prices.insert(position, 0)
            position += 1
        print(subscription_prices)
    context = {
        "subscription_prices": subscription_prices,
        "subscription_number": 0,
    }
    return render(request, 'bag/bag.html', context)


def add_to_bag(request, item_id):
    """ Add the specified product to the shopping bag """

    product = Product.objects.get(pk=item_id)
    redirect_url = request.POST.get('redirect_url')
    bag = request.session.get('bag', {})
    bag[item_id] = 'P'  # p for product

    request.session['bag'] = bag
    messages.success(request, f'Added {product.name} to your bag')
    return redirect(redirect_url)


@login_required
def add_subscription_to_bag(request, item_id):
    """ Add a specified subscription to the shopping bag """
    subscription = BookOfMonth.objects.get(pk=item_id)
    redirect_url = request.POST.get('redirect_url')
    bag = request.session.get('bag', {})
    bag[item_id] = 'S'  # s for subscription
    request.session['bag'] = bag
    messages.success(
        request, f'Added {subscription.category.friendly_name} book club subscription to your bag')
    return redirect(redirect_url)


def remove_from_bag(request, item_id):
    """Remove a product from the shopping bag"""

    try:
        product = get_object_or_404(Product, pk=item_id)
        bag = request.session.get('bag', {})
        bag.pop(item_id)
        messages.success(request, f'Removed {product.name} from your bag')

        request.session['bag'] = bag
        return HttpResponse(status=200)

    except Exception as e:
        messages.error(request, f'Error removing item: {e}')
        return HttpResponse(status=500)


def remove_subscription_from_bag(request, item_id):
    """Remove a subscription from the shopping bag"""

    try:
        user_profile = get_object_or_404(UserProfile, user=request.user)
        subscriptions_in_bag = user_profile.subscriptions_in_bag
        user_profile.subscriptions_in_bag = subscriptions_in_bag - 1
        user_profile.save()
        subscription = get_object_or_404(BookOfMonth, pk=item_id)
        bag = request.session.get('bag', {})
        bag.pop(item_id)
        messages.success(
            request, f'Removed {subscription.category.friendly_name} book club subscription to your bag')

        request.session['bag'] = bag
        return HttpResponse(status=200)

    except Exception as e:
        messages.error(request, f'Error removing item: {e}')
        return HttpResponse(status=500)
