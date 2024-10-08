# investor/urls.py

from django.urls import path

from borrower.views import CreditStatementAnalysis,CreateBorrower

urlpatterns = [
    path('borrower/credit-statement/', CreditStatementAnalysis.as_view(), name='add-fund'),
    path('borrower/create-borrower/', CreateBorrower.as_view(), name='create-borower')
    
]
