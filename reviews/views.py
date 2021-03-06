from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Review
from .forms import ReviewForm
from products.models import Product
from django.contrib import messages
# Create your views here.


@login_required
def write_review(request, product_id):
    """ Display the user's profile. """
    # Code to secure the view. If the user tries to manually enter the url to review
    # a product they already have then they are redirected
    product = get_object_or_404(Product, pk=product_id)
    try:
        user_already_reviewed = product.reviews.get(review_by=request.user)
    except:
        user_already_reviewed = False
    # user is redirected if they already reviewed the product
    if user_already_reviewed:
        messages.error(request, 'Oops you already reviewed this product')
        return redirect(reverse('product_detail', args=[product.id]))
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.review_by = request.user
            instance.product = product
            instance.save()
            messages.success(request, 'Your review was added!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request,
                           ('Failed to add review. '
                            'Please ensure the form is valid.'))
    else:
        form = ReviewForm()

    template = 'reviews/write-review.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


@login_required
def edit_review(request, product_id):
    """ Edit a user's review """
    # Code to secure the view. If the user tries to manually enter the url to review
    # a product they already have then they are redirected
    product = get_object_or_404(Product, pk=product_id)
    review = get_object_or_404(Review, product=product, review_by=request.user)
    form = ReviewForm(request.POST, instance=review)
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.review_by = request.user
            instance.product = product
            instance.save()
            messages.success(request, 'Your review was updated!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request,
                           ('Failed to update review. '
                            'Please ensure the form is valid.'))
    else:
        form = ReviewForm(instance=review)

    template = 'reviews/edit-review.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


@login_required
def delete_review(request, review_id):
    """ Delete a review from the store """

    owns_review = False
    review = get_object_or_404(
        Review, pk=review_id, review_by=request.user)
    # for redirecting the user
    product = review.product
    try:
        owns_review = get_object_or_404(
            Review, pk=review_id, review_by=request.user)
        print(owns_review)
    except:
        owns_review = False
        print(owns_review)

    if request.user.is_superuser or owns_review:
        review.delete()
        messages.success(request, 'Review deleted!')
        return redirect(reverse('product_detail', args=[product.id]))
    else:
        messages.error(
            request, 'Sorry,  you don\'t have permission to do that')
        return redirect(reverse('product_detail', args=[product.id]))
