from datetime import timedelta
from django.conf import settings

REQUIRED_USER_FIELDS = ['email', 'phone_number', 'password',"date_of_birth"]
REQUIRED_USER_FIELDS_ADDRESS = ['street_address', 'city', 'state','country','postal_code']

REQUIRED_USER_FIELDS_LOGIN = ['email', 'password']

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),  # Adjust as needed
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': "AJNUOHFUAHUDHFOUOFNF8228DA5DADA0",
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}
STRIPE_API=settings.STRIPE_SECRET_KEY