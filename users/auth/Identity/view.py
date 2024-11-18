
from enhancefund.Constant import REQUIRED_USER_FIELDS, REQUIRED_USER_FIELDS_LOGIN, STRIPE_API
from enhancefund.postvalidators import BaseValidator
from enhancefund.redisserver import set_cache_value, get_value_view
from enhancefund.rolebasedauth import BaseAuthenticatedView
from enhancefund.utils import enhance_response, create_stripe_user, \
    stripe_document_verification_update, create_stripe_customer_payment
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.response import Response
#  create user api
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from users.models import User, UserVerification

from users.serializers import UserSerializer, UserVerificationSerializer
import stripe

stripe.api_key = STRIPE_API


def extract_verification_details(verification_session):
    return {
        'status': verification_session.get('status'),
        'url': verification_session.get('url'),
    }
class IdentityVerification(BaseAuthenticatedView,generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user)
        verification_url=stripe.identity.VerificationSession.create(verification_flow="vf_1Q5BTXEATcezBu54p94l1IQ7")
        extracted_data=extract_verification_details(verification_url)
        verification_id = verification_url['id']
        user_email=serializer.data['email']
        set_cache_value(user_email, verification_id)

        return enhance_response (data=extracted_data, message="Kyc url created Successfully", status=200)

class VerificationStatus(BaseAuthenticatedView,generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user)
        stripe.api_key = STRIPE_API
        user_email=serializer.data['email']
        user_checklist=serializer.data['checklist']
        if 'KYC' in user_checklist:
            return enhance_response (data={}, message="Your Kyc is Already Verified", status=400)
        redis_data=get_value_view(user_email)
        if not redis_data:
            return enhance_response (data={}, message="Something wrong with Kyc, Please try again", status=400)
        print(redis_data,"redis")
        # redis_data={'key': 'kual@gmail.com', 'value': 'vs_1Q5CxnEATcezBu54kaTehIce'}
        verification_id = redis_data['value']
        verification_id = verification_id.decode('utf-8')

        print(verification_id,"verification_id")
        stripe_response=stripe.identity.VerificationSession.retrieve(verification_id)
        print(stripe_response,"pppppppp")
        if stripe_response["status"] == "requires_input":
            return enhance_response(data={"kyc_status": 204}, message="We are Processing Your KYC", status=200)

        if stripe_response["status"] != "verified":
            return enhance_response(data={},  message="Your Previous kyc was failed, Please try again", status=400)

        try:
            account=create_stripe_user(serializer)
            customer=create_stripe_customer_payment(serializer)


            #
            stripe_document_verification_update(account.individual.account)
            user.stripe_account_id=account.individual.account
            user.stripe_customer_id=customer.id
            user.save()
            user = request.user


            # user = User.objects.get(email=user_email)
            try:
                request_data = {
                    "verification_type": "identity",
                    "document_url": "https://example.com/document/12345.pdf",
                    "verification_status": "verified"  # Optional, default is 'pending'
                }
                # Attempt to get the UserVerification object for the given user
                user_verification = UserVerification.objects.get(user=user)

                # If found, update the existing user verification
                print(user_verification)
                serializer = UserVerificationSerializer(user_verification, data=request_data)

                if serializer.is_valid():
                    serializer.save()
                    user.checklist = ['KYC']
            except UserVerification.DoesNotExist:
                # If not found, create a new user verification object
                serializer = UserVerificationSerializer(data=request_data, context={"user": user})
                print(serializer)

                if serializer.is_valid():
                    serializer.save()
                    user.checklist = ['KYC']
                else:
                    print("not valid",serializer.errors)


        except Exception as e:
            print("Error saving user:", str(e))
            return enhance_response(data={}, message="Failed to update user", status=500)
        user.save()
        return enhance_response(data={}, message="KYC verified successfully", status=200)


    