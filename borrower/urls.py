# investor/urls.py

from django.urls import path

from borrower.views import CreditStatementAnalysis,CreateLoan

urlpatterns = [
    path('borrower/credit-statement/', CreditStatementAnalysis.as_view(), name='add-fund'),
    path('borrower/create-loan/', CreateLoan.as_view(), name='create-loan')
    
]
