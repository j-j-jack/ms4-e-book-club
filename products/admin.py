from django.contrib import admin
from .models import Product, Category, WiderCategory

# Register your models here.


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
        "category",
        "model",
        "description",
        "price",
        "rating",
        "currently_on_sale",
        "image",
        "pdf",
    )


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "friendly_name",
        "wider_category",
    )


class WiderCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "friendly_name",
    )


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(WiderCategory, WiderCategoryAdmin)
