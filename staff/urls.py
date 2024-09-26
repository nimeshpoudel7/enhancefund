from django.urls import path
from . import views

urlpatterns = [
    path('verify_documents/', views.verify_documents, name='verify_documents'),
    path('approve_borrower/<int:borrower_id>/',
         views.approve_borrower, name='approve_borrower'),
]
