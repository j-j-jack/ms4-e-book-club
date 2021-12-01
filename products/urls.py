from django.urls import path
from . import views

urlpatterns = [
    path('fiction', views.fiction, name='fiction')
]
