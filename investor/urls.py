from django.urls import path
from . import views

app_name = 'investor'

urlpatterns = [
    path('dashboard/', views.investor_dashboard, name='dashboard'),
]
