from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib import messages
import json
from products.models import Category
from .models import BookOfMonth
from .forms import BookOfMonthForm
from profiles.models import UserProfile
# Create your views here.


@login_required
def edit_book_clubs(request):
    """ Edit the book clubs """

    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))
    categories = Category.objects.all()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    category_count = categories.count()
    if is_ajax:
        response = {'finished': False, }
        category = int(request.POST['category'])
        book_of_month_instance = get_object_or_404(
            BookOfMonth, category=category)
        form = BookOfMonthForm(
            category, request.POST, instance=book_of_month_instance)
        if form.is_valid():
            form.save()
        else:
            messages.error(
                request, 'Failed to  update book clubs. Please ensure the form is valid.')
        if category == category_count:
            response = {'finished': True, }
            messages.success(request, 'Successfully updated book clubs!')

        return HttpResponse(json.dumps(response), status=200)

    forms = []
    for cat in categories:
        forms.append(BookOfMonthForm(category=cat.id, auto_id=False))

    template = 'book_clubs/edit-book-clubs.html'
    context = {
        'forms': forms,
        'category_count': category_count,
    }

    return render(request, template, context)


@login_required
def unsubscribe_next_month(request, item_id):
    """Unsubscribe from a particular book club next month"""

    book_club = BookOfMonth.objects.get(pk=item_id)
    redirect_url = request.POST.get('redirect_url')
    user_profile = get_object_or_404(UserProfile, user=request.user)
    user_profile.book_club_subscriptions_next_month.remove(book_club)
    messages.success(
        request, f'You will not be subscribed to the {book_club.friendly_name} book club next month')
    return redirect(redirect_url)


@login_required
def resubscribe_next_month(request, item_id):
    """Unsubscribe from a particular book club next month"""

    book_club = BookOfMonth.objects.get(pk=item_id)
    redirect_url = request.POST.get('redirect_url')
    user_profile = get_object_or_404(UserProfile, user=request.user)
    user_profile.book_club_subscriptions_next_month.add(book_club)
    messages.success(
        request, f'You are resubscribed to the {book_club.friendly_name} next month')
    return redirect(redirect_url)
