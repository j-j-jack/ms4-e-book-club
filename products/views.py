from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib import admin, messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from .models import Product, Category
from django.db.models import Q
from django.http import JsonResponse, FileResponse
from django.core import serializers
from .forms import ProductForm
from profiles.models import UserProfile
import os
from django.conf import settings
# Create your views here.


# Create your views here.


def products(request):
    """ A view to return the products page """
    # used to track which products displayed when loadmore is clicked
    load_round = 0
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    products = Product.objects.all()
    query = None
    categories = None
    if request.GET:
        # filter functionality using queries defined in the navbar
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
        load_more = True
        load_round = int(request.GET.get('load_round'))
        response_items = products[load_round*20: (load_round*20)+20]
        # used to make the load more button disappear if there are not more than 20 products
        # left to display
        load_more = products[(load_round*20)+20:(load_round*20)+21].exists()
        response_items = serializers.serialize('json', response_items)
        return JsonResponse({'items': response_items, 'load_more': load_more}, status=200)
    all_categories = Category.objects.all()
    all_categories = serializers.serialize('json', all_categories)
    context = {
        "products": products[0:20],
        "search_term": query,
        'current_categories': categories,
        'all_categories': all_categories,
    }
    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to show an individual product """
    # used to track which reviews are to be displayed when load more button is clicked
    load_round = 0
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    product = get_object_or_404(Product, pk=product_id)
    user_review_exists = False
    if request.user.is_authenticated:
        user_review_exists = product.reviews.filter(
            review_by=request.user).exists()
    user_review = None
    if user_review_exists:
        user_review = product.reviews.filter(review_by=request.user).first()

    all_categories = Category.objects.all()
    all_categories = serializers.serialize('json', all_categories)

    in_bag = False
    if 'bag' in request.session:
        for item in request.session['bag']:
            if int(item) == product.id:
                in_bag = True

    reviews = product.reviews.all()
    if user_review:
        # exclude the review of the current user if it exists
        # it is displayed at the top of the section for convenience
        reviews = product.reviews.all().exclude(pk=user_review.pk)
    load_more = False
    if reviews.count() > 5:
        load_more = True
    reviews = reviews[0: 5]
    if is_ajax:
        load_round = int(request.GET.get('load_round'))
        if user_review_exists:
            response_items = product.reviews.all().exclude(pk=user_review.pk)[
                load_round*5: (load_round*5)+5]
            response_items = serializers.serialize('json', response_items)
            return JsonResponse({'items': response_items}, status=200)
        else:
            response_items = product.reviews.all()[
                load_round*5: (load_round*5)+5]
        response_items = serializers.serialize('json', response_items)
        return JsonResponse({'items': response_items}, status=200)
    # used to display a download button if the user owns the book
    owns_book = False
    if request.user.is_authenticated:
        user_profile = get_object_or_404(UserProfile, user=request.user)
        owned_books = user_profile.owned_books.all()
        if product in owned_books:
            owns_book = True
    context = {
        "product": product,
        'all_categories': all_categories,
        'in_bag': in_bag,
        'reviews': reviews,
        'load_more': load_more,
        'user_review': user_review,
        'owns_book': owns_book,
    }
    return render(request, 'products/product-detail.html', context)


@login_required
def add_product(request):
    """ Add a product to the store """

    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(
                request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()

    template = 'products/add-product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    """ Edit a product in the store """

    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request,
                           ('Failed to update product. '
                            'Please ensure the form is valid.'))
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit-product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


@login_required
def delete_product(request, product_id):
    """ Delete a product from the store """

    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('products'))


@login_required
def download_product(request, product_id):
    """ Delete a product from the store """
    user_profile = get_object_or_404(UserProfile, user=request.user)
    product = get_object_or_404(Product, id=product_id)
    owned_books = user_profile.owned_books.all()
    if product in owned_books:
        obj = Product.objects.get(id=product_id)
        filename = obj.pdf.path
        response = FileResponse(open(filename, 'rb'))
        return response
    else:
        messages.error(
            request, 'Sorry, You don\'t currently own this book. Please pay for the book in order to download it')
        return redirect(reverse('home'))
