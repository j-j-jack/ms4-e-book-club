from django.contrib import admin, messages
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .models import Product, Category
from django.db.models import Q
# Create your views here.

from django.shortcuts import render

# Create your views here.


def products(request):
    """ A view to return the index page """

    products = Product.objects.all()
    query = None
    if request.GET:
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)
        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(
                    request, "You didn't enter any search criteria!")
                return redirect('products')
            queries = Q(name__icontains=query) | Q(
                description__icontains=query)
            products = products.filter(queries)

    context = {
        "products": products,
        "search_term": query
    }
    return render(request, 'products/fiction.html', context)


def product_detail(request, product_id):
    """ A view to show an individual product """

    product = get_object_or_404(Product, pk=product_id)
    context = {
        "product": product
    }
    return render(request, 'products/product-detail.html', context)
