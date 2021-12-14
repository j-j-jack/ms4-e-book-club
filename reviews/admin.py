from django.contrib import admin
from .models import Review

# Register your models here.


class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'review_by',
        'title',
        'review_body',
        'rating',
    )


admin.site.register(Review, ReviewAdmin)
