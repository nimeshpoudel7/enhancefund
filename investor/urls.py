# investor/urls.py

from django.urls import path

from investor.views import InvestorAddFunds, CheckFundStatus, WalletBalance, WithdrawBalance, InvestmentClosureProcess, \
    RecentTancation
from loans.views import PortfolioValue

urlpatterns = [
    path('investor/add-fund/', InvestorAddFunds.as_view(), name='add-fund'),
    path('investor/latest-fund-status/', CheckFundStatus.as_view(), name='fund-status'),
    path('common/wallet-balance/', WalletBalance.as_view(), name='WalletBalance'),
    path('common/withdraw-balance/', WithdrawBalance.as_view(), name='WalletBalance'),
    path('investor/portfolio-value/', PortfolioValue.as_view(), name='WalletBalance'),
    path('investor/get-return/', InvestmentClosureProcess.as_view(), name='WalletBalance'),
    path('investor/recent-transaction/', RecentTancation.as_view(), name='WalletBalance'),

]
