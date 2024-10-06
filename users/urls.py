# users/urls.py

from django.urls import path

from .auth.Identity.view import IdentityVerification, VerificationStatus
from .auth.view import CreateUserAPI, UserDetailsAPI, UserLoginAPI, CreateUserAddress, CrerateBankAccountDetails

urlpatterns = [
    path('auth/user-details/', UserDetailsAPI.as_view(), name='user-details'),
    path('auth/create-user/',CreateUserAPI.as_view(), name='create-user'),
    path('auth/login/',UserLoginAPI.as_view(), name='login-user'),
    path('auth/kyc/', IdentityVerification.as_view(), name='user-kyc'),
    path('auth/kyc-status/', VerificationStatus.as_view(), name='user-kyc-status'),
    path('auth/add-address/', CreateUserAddress.as_view(), name='user-address'),
    path('auth/add-bank-details/', CrerateBankAccountDetails.as_view(), name='user-address'),




]
