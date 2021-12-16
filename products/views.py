from django.shortcuts import render
from django.contrib import admin, messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .models import Product, Category
from django.db.models import Q
from django.http import JsonResponse
from django.core import serializers
from .forms import ProductForm
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

    load_round = 0
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    product = get_object_or_404(Product, pk=product_id)
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

    review_count = product.reviews.count()
    print(review_count)
    reviews = product.reviews.all()
    if user_review:
        reviews = product.reviews.all().exclude(pk=user_review.pk)
    load_more = False
    if reviews.count() > 5:
        load_more = True
    reviews = reviews[0: 5]
    if is_ajax:
        load_round = int(request.GET.get('load_round'))
        # exclude users own review if exists as it is at the top
        response_items = product.reviews.all().exclude(pk=user_review.pk)[
            load_round*5: (load_round*5)+5]
        response_items = serializers.serialize('json', response_items)
        return JsonResponse({'items': response_items}, status=200)
    context = {
        "product": product,
        'all_categories': all_categories,
        'in_bag': in_bag,
        'reviews': reviews,
        'load_more': load_more,
        'user_review': user_review,
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
