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
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=product)
        if form.is_valid():
            form.save(commit=False)
            form.user = request.user
            form.product = product
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request,
                           ('Failed to update product. '
                            'Please ensure the form is valid.'))
    else:
        form = ReviewForm()

    template = 'reviews/write-review.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)
