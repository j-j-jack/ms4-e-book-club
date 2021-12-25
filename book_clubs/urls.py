from django.urls import path
from . import views

urlpatterns = [
    path('edit', views.edit_book_clubs, name='edit'),
    path('unsubscribe_next_month/<item_id>',
         views.unsubscribe_next_month, name='unsubscribe_next_month'),
    path('resubscribe_next_month/<item_id>',
         views.resubscribe_next_month, name='resubscribe_next_month'),
    path('fiction', views.fiction_book_clubs, name='fiction_clubs'),
    path('non_fiction', views.non_fiction_book_clubs, name='non_fiction_clubs'),
    path('child_teen', views.child_teen_book_clubs, name='child_teen_clubs'),

]
