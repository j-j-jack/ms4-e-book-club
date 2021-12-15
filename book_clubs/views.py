from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib import messages

from products.models import Category
from .models import BookOfMonth
from .forms import BookOfMonthForm
# Create your views here.


@login_required
def edit_book_clubs(request):
    """ Add a product to the store """

    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))
    categories = Category.objects.all()
    if request.method == 'POST':
        print(request.POST)
        book_of_month_instance = get_object_or_404(BookOfMonth, category=1)
        print(book_of_month_instance)
        form = BookOfMonthForm(
            1, request.POST, instance=book_of_month_instance)
        print(form)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated book clubs!')
            return redirect(reverse('home'))
        else:
            messages.error(
                request, 'Failed to  update book clubs. Please ensure the form is valid.')
    forms = []
    for category in categories:
        forms.append(BookOfMonthForm(category=category.id))

    template = 'book_clubs/edit-book-clubs.html'
    context = {
        'forms': forms,
    }

    return render(request, template, context)
