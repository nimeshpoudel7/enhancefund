# loans/urls.py

from django.urls import path

from loans.views import CreateLoan, ViewLoan, loanList, createInvestment, expectedReturn, myInvestment, \
    checkRepaymentBorrower, loanRepayment, checkRefundStatus

urlpatterns = [
    path('loan/create-loan/', CreateLoan.as_view(), name='Create-loan'),
    path('loan/view-loan/', ViewLoan.as_view(), name='view-own-loan'),
    path('loan/loan-list/', loanList.as_view(), name='view-all-loan'),
    path('loan/create-investment/', createInvestment.as_view(), name='view-all-loan'),
    path('loan/expected-return/', expectedReturn.as_view(), name='view-return-loan'),
    path('loan/my-investment/', myInvestment.as_view(), name='view-my-loan'),
    path('loan/check-repayment/', checkRepaymentBorrower.as_view(), name='view-check-history'),
    path('loan/loan-repayment/', loanRepayment.as_view(), name='view-check-history'),
    path('loan/payment-status/', checkRefundStatus.as_view(), name='view-check-history'),

]
