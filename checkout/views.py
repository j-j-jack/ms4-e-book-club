from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from .forms import OrderForm
from bag.contexts import bag_contents
import stripe

# Create your views here.


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, 'There\'s nothing in your bag at the moment')
        return redirect(reverse('products'))

    current_bag = bag_contents(request)
    total = current_bag['grand_total']
    stripe_total = round(total*100)
    stripe.api_key = stripe_secret_key
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )
    print(intent)
    order_form = OrderForm()
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': 'pk_test_51JuFnYI4BS1eZU3SIsKermObhM6u66B1qvAcARQ3GTosE5dQOmJtXSXTDbwgE19kbnvemlnTRT9kiCWODvcITjm900gs8Pw8dQ',
        'client secret': 'test client secret',
    }

    return render(request, template, context)
