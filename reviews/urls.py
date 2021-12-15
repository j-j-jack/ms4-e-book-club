from django.urls import path
from . import views

urlpatterns = [
    path('write_review/<int:product_id>/',
         views.write_review, name='write_review'),
    path('edit_review/<int:product_id>/',
         views.edit_review, name='edit_review'),
]
