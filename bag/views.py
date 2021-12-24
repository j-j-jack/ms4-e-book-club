from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    render, redirect, reverse, HttpResponse, get_object_or_404
)
from django.contrib import messages
from book_clubs.models import BookOfMonth

from products.models import Product
from profiles.models import UserProfile


def view_bag(request):
    """ A view to return the index page """

    return render(request, 'bag/bag.html')


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
    """ Add a quantity of the specified product to the shopping bag """
    subscription = BookOfMonth.objects.get(pk=item_id)
    redirect_url = request.POST.get('redirect_url')
    bag = request.session.get('bag', {})
    bag[item_id] = 'S'  # s for subscription
    request.session['bag'] = bag
    messages.success(
        request, f'Added {subscription.category.friendly_name} book club subscription to your bag')
    return redirect(redirect_url)


def remove_from_bag(request, item_id):
    """Remove the item from the shopping bag"""

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
    """Remove the item from the shopping bag"""

    try:
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
