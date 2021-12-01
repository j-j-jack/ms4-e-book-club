from django.contrib import admin, messages
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .models import Product, Category
from django.db.models import Q
from django. http import JsonResponse
from django.core import serializers
# Create your views here.

from django.shortcuts import render

# Create your views here.


def products(request):
    """ A view to return the products page """

    load_round = 0
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        load_round = int(request.GET.get('load_round'))*2
        response_items = Product.objects.all()[load_round: load_round+3]
        response_items = serializers.serialize('json', response_items)
        return JsonResponse({'items': response_items}, status=200)

    products = Product.objects.all()[load_round: load_round+2]
    query = None
    categories = None
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
        "search_term": query,
        'current_categories': categories,
    }
    return render(request, 'products/fiction.html', context)


def product_detail(request, product_id):
    """ A view to show an individual product """

    product = get_object_or_404(Product, pk=product_id)
    context = {
        "product": product
    }
    return render(request, 'products/product-detail.html', context)
