# users/urls.py

from django.urls import path
from .views import UserDetailsAPI, CreateUserAPI

urlpatterns = [
    path('users/', UserDetailsAPI.as_view(), name='user-details'),
    path('create-user/',CreateUserAPI.as_view(), name='create-user')
]
