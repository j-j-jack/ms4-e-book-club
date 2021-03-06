from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_bag, name='view_bag'),
    path('add/<item_id>', views.add_to_bag, name='add_to_bag'),
    path('add_subscription/<item_id>', views.add_subscription_to_bag,
         name='add_sub_to_bag'),
    path('remove/<item_id>/', views.remove_from_bag, name='remove_from_bag'),
    path('remove_sub/<item_id>/',
         views.remove_subscription_from_bag, name='remove_sub_from_bag')
]
