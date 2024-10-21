from datetime import timedelta
from django.conf import settings

REQUIRED_USER_FIELDS = ['email', 'phone_number', 'password',"date_of_birth"]
REQUIRED_USER_FIELDS_ADDRESS = ['street_address', 'city', 'state','country','postal_code']
REQUIRED_ADD_FUND_FIELDS = ['amount']


REQUIRED_USER_FIELDS_LOGIN = ['email', 'password']
REQUIRED_CREATE_BORROWER_FIELD= ['employment_status', 'annual_income']
REQUIRED_CREATE_LOAN_FIELD= ['amount', 'term_months','loan_purpose']
REQUIRED_CREATE_INVESTMENT_FIELD= ['amount','loan']
REQUIRED_LOAN_REPAYMENT_FIELD= ['loan_id','repayment_id']




REQUIRED_BANK_ACCOUNT_FIELD=['account_holder_name','routing_number','account_number','account_type']

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),  # Adjust as needed
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': "AJNUOHFUAHUDHFOUOFNF8228DA5DADA0",
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}
STRIPE_API='sk_test_51Q5A6eEATcezBu54bc2ohQMdGtlIH1bsB1VKKL1pBskycmzgjEdBQseDKlKa6QZQOov9yvhadioOvI7GFzACyHbV00BYYHlJU1'