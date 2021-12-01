from django.contrib import admin
from django.shortcuts import get_object_or_404, render
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


def product_detail(request, product_id):
    """ A view to show an individual product """

    product = get_object_or_404(Product, pk=product_id)
    context = {
        "product": product
    }
    return render(request, 'products/product-detail.html', context)
