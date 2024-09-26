
from enhancefund.Constant import REQUIRED_USER_FIELDS
from enhancefund.postvalidators import BaseValidator
from enhancefund.utils import enhance_response
from .models import User
from .serializers import UserSerializer
from rest_framework import status

from rest_framework import generics
from .models import User
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.response import Response
#  create user api
from django.contrib.auth.models import Group


class CreateUserAPI(generics.CreateAPIView, BaseValidator):

    def post(self, request, *args, **kwargs):

        validation_errors = self.validate_data(request.data,REQUIRED_USER_FIELDS)
        print(request.data, "aaddda")

        if validation_errors:
            return enhance_response(data=validation_errors,status=0,message="User creation eror")

        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user=serializer.save()
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
class UserDetailsAPI(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        users = self.get_queryset()
        serializer = self.get_serializer(users, many=True)
        return enhance_response (data=serializer.data, message="Users retrieved successfully", status=200)