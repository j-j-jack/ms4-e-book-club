from django.contrib import admin
from django.shortcuts import render
from .models import Product
# Create your views here.

from django.shortcuts import render

# Create your views here.


def fiction(request):
    """ A view to return the index page """

    products = Product.objects.all()
    context = {
        "products": products
    }
    return render(request, 'products/fiction.html', context)
