from django.shortcuts import render, redirect

# Create your views here.


def view_bag(request):
    """ A view to return the index page """

    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """

    redirect_url = request.POST.get('redirect_url')
    bag = request.session.get('bag', {})
    bag[item_id] = 1

    request.session['bag'] = bag
    print(request.session['bag'])
    return redirect(redirect_url)
