from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from book_clubs.models import BookOfMonth
from products.models import Product


def bag_contents(request):

    bag_items = []
    total = 0
    product_count = 0
    bag = request.session.get('bag', {})

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
            book_club_subscription = get_object_or_404(BookOfMonth, pk=item_id)
            total += 2
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
