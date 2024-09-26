from datetime import timedelta

REQUIRED_USER_FIELDS = ['email', 'phone_number', 'password']
REQUIRED_USER_FIELDS_LOGIN = ['email', 'password']

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),  # Adjust as needed
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': "AJNUOHFUAHUDHFOUOFNF8228DA5DADA0",
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}