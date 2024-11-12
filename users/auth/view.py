import stripe

from enhancefund.Constant import REQUIRED_USER_FIELDS, REQUIRED_USER_FIELDS_LOGIN, REQUIRED_USER_FIELDS_ADDRESS, \
    REQUIRED_BANK_ACCOUNT_FIELD
from enhancefund.postvalidators import BaseValidator
from enhancefund.rolebasedauth import BaseAuthenticatedView
from enhancefund.utils import enhance_response, stripe_external_bank_account
from ..models import User, UserAddress, UserBankDetails
from ..serializers import UserSerializer, UserAddressSerializer, UserBankDetailsSerializer
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.response import Response
#  create user api
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token


class CreateUserAPI(generics.CreateAPIView, BaseValidator):

    def post(self, request, *args, **kwargs):

        validation_errors = self.validate_data(request.data,REQUIRED_USER_FIELDS)
        print(request.data, "aaddda")

        if validation_errors:
            return enhance_response(data=validation_errors,status=status.HTTP_400_BAD_REQUEST,message="User creation eror")

        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user=serializer.save()
            user.checklist=['Register']
            user.save()
            role = request.data.get('role')

            if role:
                # Create the group if it doesn't exist
                group, created = Group.objects.get_or_create(name=role.capitalize())

                # Add the user to the group
                user.groups.add(group)

                # If you want to set permissions for the group, you can do it here
                # For example:
                # if created:
                #     permission = Permission.objects.get(codename='can_view_financial_data')
                #     group.permissions.add(permission)
            return enhance_response(data=serializer.data, status=status.HTTP_201_CREATED,message="User created successfully")
        return enhance_response( status=status.HTTP_400_BAD_REQUEST,message=serializer.get_error_message())


# ListCreateAPIView
# get login user details
class UserLoginAPI(generics.GenericAPIView,BaseValidator):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def post(self, request, *args, **kwargs):
        try:

            validation_errors = self.validate_data(request.data,REQUIRED_USER_FIELDS_LOGIN)

            if validation_errors:
                return enhance_response(data=validation_errors,status=0,message="login error, please try again")

            username = request.data.get('email')
            password = request.data.get('password')

            user = authenticate(username=username, password=password)
            if user:
                token, created = Token.objects.get_or_create(user=user)
                print("token",token)
                data = {
                    'user': self.get_serializer(user).data,
                    'token': f"Token {token.key}"
                    }
                return enhance_response(data=data, status=status.HTTP_200_OK, message="Login successful")
            else:
                return enhance_response(status=status.HTTP_401_UNAUTHORIZED, message="Invalid credentials")
        except:
            return enhance_response(status=status.HTTP_401_UNAUTHORIZED, message="Invalid credentials")


class UserDetailsAPI(BaseAuthenticatedView,generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user)
        return enhance_response (data=serializer.data, message="Users retrieved successfully", status=200)

class CreateUserAddress(BaseAuthenticatedView,generics.CreateAPIView, BaseValidator):
    def post(self, request, *args, **kwargs):
        queryset = User.objects.all()

        # Validate the required fields
        validation_errors = self.validate_data(request.data, REQUIRED_USER_FIELDS_ADDRESS)
        if validation_errors:
            return enhance_response(data=validation_errors, status=status.HTTP_400_BAD_REQUEST,
                                    message="Please enter required fields")

        user = request.user
        user_id = User.objects.get(email=user.email)  # Correct way to get user by email

        # Extract address data from the request
        address_data = {
            'street_address': request.data.get('street_address'),
            'city': request.data.get('city'),
            'state': request.data.get('state'),
            'country': request.data.get('country'),
            'postal_code': request.data.get('postal_code'),
        }

        try:
            # Try to get the existing user address
            user_address = UserAddress.objects.get(user=user_id)
            # If address exists, update it
            serializer = UserAddressSerializer(user_address, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return enhance_response(data=serializer.data, status=status.HTTP_200_OK,
                                        message="Address updated successfully")
            else:
                return enhance_response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST,
                                        message="Invalid data")

        except UserAddress.DoesNotExist:
            # If no address exists, create a new one
            serializer = UserAddressSerializer(data=request.data, context={"user": user_id})
            if serializer.is_valid():
                serializer.save()
                return enhance_response(data=serializer.data, status=status.HTTP_201_CREATED,
                                        message="Address created successfully")
            else:
                return enhance_response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST,
                                        message="Invalid data")

class CrerateBankAccountDetails(BaseAuthenticatedView,generics.CreateAPIView,BaseValidator):
    def post(self, request, *args, **kwargs):
        bank_account_data = {
            'object': 'bank_account',
            'account_holder_name': request.data.get('account_holder_name'),
            'account_type': request.data.get('account_holder_type'),
            'routing_number': request.data.get('routing_number'),
            'account_number': '000123456789',
            'country':'CA',
            'currency': 'CAD',
            'account_holder_type':'individual'
        }
        # Validate the request data for required fields
        validation_errors = self.validate_data(request.data, REQUIRED_BANK_ACCOUNT_FIELD)
        if validation_errors:
            return enhance_response(data=validation_errors, status=status.HTTP_400_BAD_REQUEST,
                                    message="Please enter required fields")

        user = request.user

        try:
            print(request.data)
            # Check if bank details for the user already exist
            user_bankdetails = UserBankDetails.objects.get(user=user)

            # If details exist, update the existing record
            serializer = UserBankDetailsSerializer(user_bankdetails, data=request.data, partial=True,
                                                   context={"user": user})
            if serializer.is_valid():
                serializer.save()
                user.checklist = ['BANK_ACCOUNT']  # Add 'BANK_ACCOUNT' to the user's checklist
                user.save()  # Ensure changes to user checklist are saved
                stripe_external_bank_account(user.stripe_account_id,bank_account_data)
                return enhance_response(data=serializer.data, message="Bank Details Updated Successfully", status=200)

            else:
                return enhance_response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST,
                                        message="Invalid data")

        except UserBankDetails.DoesNotExist:
            # If no bank details exist, create a new record
            serializer = UserBankDetailsSerializer(data=request.data, context={"user": user})
            if serializer.is_valid():
                serializer.save()
                user.checklist = ['BANK_ACCOUNT']  # Add 'BANK_ACCOUNT' to the user's checklist
                user.save()  # Ensure changes to user checklist are saved

                stripe_external_bank_account(user.stripe_account_id,bank_account_data)
                return enhance_response(data=serializer.data, message="Bank Details Added Successfully", status=200)
            else:
                return enhance_response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST,
                                        message="Invalid data")

        # stripe_bank=stripe.Account.create_external_account.(,
        # {})
        return enhance_response(data={}, message="Unexpected Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

