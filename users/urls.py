# users/urls.py

from django.urls import path
from .auth.view import CreateUserAPI,UserDetailsAPI,UserLoginAPI
urlpatterns = [
    path('auth/user-details/', UserDetailsAPI.as_view(), name='user-details'),
    path('auth/create-user/',CreateUserAPI.as_view(), name='create-user'),
    path('auth/login/',UserLoginAPI.as_view(), name='login-user')
]
