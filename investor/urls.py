# investor/urls.py

from django.urls import path

from investor.views import InvestorAddFunds, CheckFundStatus, WalletBalance, WithdrawBalance

urlpatterns = [
    path('investor/add-fund/', InvestorAddFunds.as_view(), name='add-fund'),
    path('investor/latest-fund-status/', CheckFundStatus.as_view(), name='fund-status'),
    path('investor/wallet-balance/', WalletBalance.as_view(), name='WalletBalance'),
    path('investor/withdraw-balance/', WithdrawBalance.as_view(), name='withdraw balance'),

]
