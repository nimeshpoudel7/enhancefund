
from enhancefund.Constant import REQUIRED_USER_FIELDS, REQUIRED_USER_FIELDS_LOGIN, STRIPE_API
from enhancefund.postvalidators import BaseValidator
from enhancefund.redisserver import set_cache_value, get_value_view
from enhancefund.rolebasedauth import BaseAuthenticatedView
from enhancefund.utils import enhance_response, create_stripe_user
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.response import Response
#  create user api
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from users.models import User

from users.serializers import UserSerializer
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
        # if 'KYC' in user_checklist:
        #     return enhance_response (data={}, message="Your Kyc is Already Verified", status=400)
        # redis_data=get_value_view(user_email)
        # if not redis_data:
        #     return enhance_response (data={}, message="Something wrong with Kyc, Please try again", status=400)
        # print(redis_data)
        redis_data={'key': 'kual@gmail.com', 'value': 'vs_1Q5CxnEATcezBu54kaTehIce'}
        verification_id = redis_data['value']
        stripe_response=stripe.identity.VerificationSession.retrieve(verification_id)
        # print(stripe_response)
        # if stripe_response["status"] != "verified":
        #     return enhance_response(data={},  message="Your Previous kyc was failed, Please try again", status=400)
        # user.checklist = ['KYC']
        # create stripe user
        # UserVerification
        try:
            create_stripe_user(serializer)
            print("hereee")
            user.save()  # Save the user and check for issues
            print("User updated successfully.")
        except Exception as e:
            print("Error saving user:", str(e))
            return enhance_response(data={}, message="Failed to update user", status=500)

        return enhance_response(data={}, message="KYC verified successfully", status=200)


    