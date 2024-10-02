from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from enhancefund.commonserializer import CommonSerializer
from .models import User, UserAddress, UserVerification


class UserSerializer(CommonSerializer):
    date_of_birth = serializers.DateField(input_formats=['%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y'])
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [ 'email', 'phone_number', 'password', 'confirm_password','role', 'status', 'stripe_customer_id',
                  'created_at', 'updated_at','checklist','date_of_birth','first_name','last_name']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        # Validate the password
        validate_password(attrs['password'])

        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            confirm_password = validated_data.pop('confirm_password', None)
            if password != confirm_password:
                raise serializers.ValidationError({"password": "Password fields didn't match."})
            instance.set_password(password)
        return super().update(instance, validated_data)


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = ['street_address', 'city', 'state', 'country', 'postal_code']

    def create(self, validated_data):
        # Retrieve the user from context
        user = self.context.get('user')

        if not user:
            raise serializers.ValidationError("User not found in context")

        # Create the address and associate it with the user
        return UserAddress.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        # Update the address instance
        instance.street_address = validated_data.get('street_address', instance.street_address)
        instance.city = validated_data.get('city', instance.city)
        instance.state = validated_data.get('state', instance.state)
        instance.country = validated_data.get('country', instance.country)
        instance.postal_code = validated_data.get('postal_code', instance.postal_code)
        instance.save()
        return instance

class UserVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserVerification
        fields = ['verification_status']

    def create(self, validated_data):
        # Retrieve the user from context
        user = self.context.get('user')

        if not user:
            raise serializers.ValidationError("User not found in context")

        # Create the address and associate it with the user
        return UserVerification.objects.create(user=user, **validated_data)





