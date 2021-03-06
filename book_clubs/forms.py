from django import forms
from .models import BookOfMonth
from products.models import Product


class BookOfMonthForm(forms.ModelForm):
    """form used for editing the books of the month"""
    class Meta:
        model = BookOfMonth
        fields = ('book', 'description')
        exclude = ('reviews', 'sales_count', 'rating')

    def __init__(self, category, *args, **kwargs):
        super().__init__(*args, **kwargs)
        products = Product.objects.filter(category=category)
        names = [(c.id, c.get_name()) for c in products]
        self.fields['book'].choices = names
        self.fields['book'].label = products[0].category.friendly_name + ' Book Club'
        self.fields['description'].label = 'Description why...'
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'
