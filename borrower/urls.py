from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'borrower'

urlpatterns = [
    path('apply/', views.apply_for_loan, name='apply'),
]
