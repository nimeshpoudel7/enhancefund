
from enhancefund.Constant import REQUIRED_USER_FIELDS, REQUIRED_USER_FIELDS_LOGIN, REQUIRED_USER_FIELDS_ADDRESS
from enhancefund.postvalidators import BaseValidator
from enhancefund.rolebasedauth import BaseAuthenticatedView
from enhancefund.utils import enhance_response
from ..models import User, UserAddress
from ..serializers import UserSerializer, UserAddressSerializer
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

        validation_errors = self.validate_data(request.data,REQUIRED_USER_FIELDS_LOGIN)

        if validation_errors:
            return enhance_response(data=validation_errors,status=0,message="login error, please try again")

        username = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        print("aaa",user.id)
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

        validation_errors = self.validate_data(request.data,REQUIRED_USER_FIELDS_ADDRESS)
        print("here")
        if validation_errors:
            return enhance_response(data=validation_errors,status=status.HTTP_400_BAD_REQUEST,message="Please enter requried field")
        user = request.user
        user_id = User.objects.get(email=user)

        print("aaaaaaaaaa",user_id)

        # user = User.objects.get(email=user_email)
        print("bbbbbb",user.id)
        address_data = {
            'street_address': request.data.get('street_address'),
            'city': request.data.get('city'),
            'state': request.data.get('state'),
            'country': request.data.get('country'),
            'postal_code': request.data.get('postal_code'),
        }
        try:
            user_address = UserAddress.objects.get(user=user)
            # If found, update the existing address
            serializer = UserAddressSerializer(user_address, data=request.data)
        except UserAddress.DoesNotExist:
            # If not found, create a new address
            serializer = UserAddressSerializer(data=request.data,context={"user":user})

        if serializer.is_valid():
            serializer.save()
            return enhance_response(data=serializer.data, status=status.HTTP_201_CREATED,
                                    message="Address created successfully")
        else:
            return enhance_response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST, message="Invalid data")



