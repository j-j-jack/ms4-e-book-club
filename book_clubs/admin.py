from django.contrib import admin
from .models import BookOfMonth

# Register your models here.


class BookOfMonthAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "friendly_name",
    )


admin.site.register(BookOfMonth, BookOfMonthAdmin)
