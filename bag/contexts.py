from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from book_clubs.models import BookOfMonth
from products.models import Product
from profiles.models import UserProfile
import decimal


def bag_contents(request):

    bag_items = []
    total = 0
    product_count = 0
    bag = request.session.get('bag', {})
    user_profile = None
    user_subscription_count = 0
    if request.user.is_authenticated:
        user_profile = get_object_or_404(UserProfile,  user=request.user)
        user_subscription_count = user_profile.book_club_subscriptions_this_month.all().count()
        user_profile.subscriptions_in_bag = 0
    for item_id, type in bag.items():
        if type == 'P':
            product = get_object_or_404(Product, pk=item_id)
            total += product.price
            product_count += 1
            bag_items.append({
                'item_id': item_id,
                'item_id_as_int': int(item_id),
                'type': 'product',
                'product': product,
                'book_club': None,
            })
        elif type == 'S':

            user_profile.subscriptions_in_bag += 1
            user_profile.save()
            print('user subscriptions in bag')
            print(user_profile.subscriptions_in_bag)
            book_club_subscription = get_object_or_404(BookOfMonth, pk=item_id)
            if user_subscription_count < 2:
                total = total + 2
                book_club_subscription.price = 2
                book_club_subscription.save()
            elif user_subscription_count >= 2 and user_subscription_count < 4:
                total = total + decimal.Decimal(1.75)
                book_club_subscription.price = decimal.Decimal(1.75)
                book_club_subscription.save()
            else:
                total = total + decimal.Decimal(1.50)
                book_club_subscription.price = decimal.Decimal(1.50)
                book_club_subscription.save()
            user_subscription_count += 1
            print(str(user_subscription_count) + "= subscription_count")
            product_count += 1
            bag_items.append({
                'item_id': item_id,
                'item_id_as_int': int(item_id),
                'type': 'subscription',
                'product': None,
                'book_club': book_club_subscription,
            })

    grand_total = total

    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'grand_total': grand_total,
    }

    return context
