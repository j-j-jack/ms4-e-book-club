from django.contrib import admin
from .models import Order, OrderLineItemProduct, OrderLineItemSubscription


class OrderLineItemAdminInline(admin.TabularInline):
    model = OrderLineItemProduct
    readonly_fields = ('lineitem_total',)


class OrderLineItemAdminInline(admin.TabularInline):
    model = OrderLineItemSubscription
    readonly_fields = ('lineitem_total',)


class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineItemAdminInline,)

    readonly_fields = ('order_number', 'date',
                       'grand_total', 'original_bag')

    fields = ('order_number', 'user_profile', 'date', 'full_name',
              'email', 'phone_number', 'country',
              'postcode', 'town_or_city', 'street_address1',
              'street_address2', 'county', 'grand_total', 'original_bag',)

    list_display = ('order_number', 'date', 'full_name',
                    'grand_total',)

    ordering = ('-date',)


admin.site.register(Order, OrderAdmin)
