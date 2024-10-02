from rest_framework.response import Response
import stripe
from datetime import datetime

from users.models import UserAddress,User


def enhance_response(data=None, message=None, status=None):
    response_data = {
        "code": 1 if status in [200, 201, 204] else 0, 
        "message": message if message else "Request was successful" if status else "Request failed",
        "data": data,
    }
    return Response(response_data, status=status)

def create_stripe_user(serializer):
    try:
        user_email = serializer.data['email']
        role = serializer.data['role']
        phone = serializer.data['phone_number']
        user = User.objects.get(email=user_email)
        user_address = UserAddress.objects.get(user=user.id)

        # {street_address: '369 roal york', city: 'city .', state: 'ste is required.', country: 'county is required.',
        #  postal_code: 'MXC RCT'}
        # vvv
        street_address = user_address.street_address
        city = user_address.city
        postal_code = user_address.postal_code
        state = user_address.state
        country = user_address.country

        date_of_birth = serializer.data['date_of_birth']
        print(user_email)
        dob = datetime.strptime(str(date_of_birth), '%Y-%m-%d')

        account = stripe.Account.create(
            country="CA",
            type="custom",
            default_currency="CAD",
            business_type="individual",
            email=user_email,
            capabilities={
                "transfers": {"requested": True},
                "card_payments": {"requested": True}
            },
            individual={
                "address": {
                    "line1": street_address,
                    "city": city,
                    "state": "ON",
                    "country": "CA",
                    "postal_code": "M8Y 2R1"
                },
                "email": user_email,
                "first_name": "final",
                "last_name": "Poudel",
                "phone": "4379552968",
                "id_number": "000000000",  # Ensure this is valid
                # "job_title": ,
                "dob": {
                    "day": dob.day,
                    "month": dob.month,
                    "year": dob.year
                },
                "relationship":{
                    "title":role,
                }
            },
            business_profile={
                "url": "www.codehimalaya.com",
                "mcc": "1520",
                "product_description": "Enhance fund user"
            },
        )

        return account

    except stripe.error.StripeError as e:
        # Log the error details for debugging
        print(f"Stripe Error: {str(e)}")
        raise e

    except Exception as e:
        # Log any other exception
        print(f"Error during account creation: {str(e)}")
        raise e
