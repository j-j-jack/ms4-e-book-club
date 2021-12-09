from django.shortcuts import render
from django.contrib import admin, messages
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .models import Product, Category
from django.db.models import Q
from django. http import JsonResponse
from django.core import serializers
# Create your views here.


# Create your views here.


def products(request):
    """ A view to return the products page """

    load_round = 0
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    products = Product.objects.all()
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

    if is_ajax:
        load_round = int(request.GET.get('load_round'))
        response_items = products[load_round*20: (load_round*20)+20]
        response_items = serializers.serialize('json', response_items)
        return JsonResponse({'items': response_items}, status=200)
    #products = products[0: 3]
    all_categories = Category.objects.all()
    all_categories = serializers.serialize('json', all_categories)
    context = {
        "products": products,
        "search_term": query,
        'current_categories': categories,
        'all_categories': all_categories,
    }
    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to show an individual product """

    product = get_object_or_404(Product, pk=product_id)
    all_categories = Category.objects.all()
    all_categories = serializers.serialize('json', all_categories)

    in_bag = False
    if 'bag' in request.session:
        for item in request.session['bag']:
            if int(item) == product.id:
                in_bag = True

    context = {
        "product": product,
        'all_categories': all_categories,
        'in_bag': in_bag,
    }
    return render(request, 'products/product-detail.html', context)
