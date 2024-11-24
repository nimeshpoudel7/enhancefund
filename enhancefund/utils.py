from rest_framework.response import Response
import stripe
from datetime import datetime

from users.models import UserAddress,User
from django.conf import settings
import os

def enhance_response(data=None, message=None, status=None):
    response_data = {
        "code": 1 if status in [200, 201, 204] else 0, 
        "message": message if message else "Request was successful" if status else "Request failed",
        "data": data,
    }
    return Response(response_data, status=status)
def create_stripe_customer_payment(serializer):
    user_email = serializer.data['email']
    last_name = serializer.data['last_name']
    first_name = serializer.data['first_name']
    name=first_name+" "+last_name
    investor_customer = stripe.Customer.create(
        email=user_email,
        name=name
    )
    return  investor_customer


def create_stripe_user(serializer):
    try:
        user_email = serializer.data['email']
        last_name = serializer.data['last_name']
        first_name = serializer.data['first_name']
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
                    "state": state,
                    "country": country,
                    "postal_code": postal_code
                },
                "email": user_email,
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "id_number": "000000000",  # Ensure this is valid
                # "job_title": ,
                "dob": {
                    "day": dob.day,
                    "month": dob.month,
                    "year": dob.year
                },
                "relationship":{
                    "title":role,
                },
                # "verification": {
                #     "document": {
                #         "front": dummy_stripe_file.id,
                #         "back": dummy_stripe_file2.id
                #     },
                #     # "additional_document": {
                #     #     "front": dummy_stripe_file.id,
                #     #     "back": dummy_stripe_file2.id
                #     # }
                # }
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

def stripe_document_verification_update(account_Number):
    print(account_Number)
    dummy_image_path = os.path.join(settings.BASE_DIR, 'enhancefund', 'cas.png')
    dummy_image_path2 = os.path.join(settings.BASE_DIR, 'enhancefund', 'bmi2.png')
    with open(dummy_image_path, 'rb') as dummy_file:
        address_verification = stripe.File.create(
            purpose='additional_verification',
            file=dummy_file,
            stripe_account=account_Number,
        )
        #
        with open(dummy_image_path2, 'rb') as dummy_file:
            identity_verificaton = stripe.File.create(
                purpose='identity_document',
                file=dummy_file,
                stripe_account=account_Number,
            )
            with open(dummy_image_path2, 'rb') as dummy_file:
                identity_verificaton2 = stripe.File.create(
                    purpose='identity_document',
                    file=dummy_file,
                    stripe_account=account_Number,
                )
        print(identity_verificaton)
        stripe.Account.modify(
            account_Number,
            individual={"verification":
                            {"document":
                                 {"front": identity_verificaton.id,
                                  "back":identity_verificaton2.id
                                 },
                             "additional_document":{
                                 "front": address_verification.id
                             }
                            }
                        },
        )

def stripe_external_bank_account(acc_number,data):
   stripe.Account.create_external_account(acc_number,external_account=data)
   stripe.Account.modify(
       acc_number,
       tos_acceptance={"date": 1609798905, "ip": "8.8.8.8"},
       settings={
           'payouts': {
               'schedule': {
                   'interval': 'manual',  # Set to 'manual' to disable automatic payouts
               }
           }
       }
   )




def create_payment_link_for_customer(customer_id, amount, installment_id):
    try:
        success_url = ""
        cancel_url = ""

        if installment_id == "xvKjmlKNp11":
            success_url =    f"http://localhost:3003/page/investor/success.html?ins_id={installment_id}&session_id={{CHECKOUT_SESSION_ID}}"
            cancel_url = f"http://localhost:3003/page/investor/fail.html?session_id={{CHECKOUT_SESSION_ID}}"
        else:
            success_url =     f"http://localhost:3003/page/Borrower/success.html?ins_id={installment_id}&session_id={{CHECKOUT_SESSION_ID}}"
            cancel_url = f"http://localhost:3003/page/borrower/fail.html?session_id={{CHECKOUT_SESSION_ID}}"
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': "CAD",
                    'unit_amount': int(amount * 100),  # Convert to cents
                    'product_data': {
                        'name': 'Wallet Top-Up',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            # Use checkout_session.id for URLs
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return checkout_session
    except stripe.error.StripeError as e:
        print(f"Error creating payment link: {str(e)}")
        return None


def check_Add_fund_status(payment_id):
   payment_details= stripe.checkout.Session.retrieve(
        payment_id,
    )
   return payment_details


def format_details(data):
    # Wrap each value in a dictionary with key '0'
    return {key: {"0": value} for key, value in data.items()}


def transfer_funds(amount, connected_account_id):
    try:
        transfer = stripe.Transfer.create(
            amount=int(amount * 100),
            currency="CAD",
            destination=connected_account_id,
            description="Transfer to connected account"
        )
        return transfer
    except Exception as e:
        print(f"Error during transfer: {e}")
        return None


def create_payout(amount, connected_account_id):
    try:
        payout = stripe.Payout.create(
            amount=int(amount * 100),  # Amount in cents
            currency='CAD',
            stripe_account=connected_account_id  # The connected account's ID
        )
        return payout
    except stripe.error.StripeError as e:
        return str(e)





