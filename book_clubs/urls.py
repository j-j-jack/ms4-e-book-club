from django.urls import path
from . import views

urlpatterns = [
    path('edit', views.edit_book_clubs, name='edit'),

]
