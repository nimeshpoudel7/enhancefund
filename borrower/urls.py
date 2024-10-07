# investor/urls.py

from django.urls import path

from borrower.views import CreditStatementAnalysis

urlpatterns = [
    path('borrower/credit-statement/', CreditStatementAnalysis.as_view(), name='add-fund')
]
