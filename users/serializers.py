from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from enhancefund.commonserializer import CommonSerializer
from .models import User


class UserSerializer(CommonSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [ 'email', 'phone_number', 'password', 'confirm_password', 'role', 'status', 'stripe_customer_id',
                  'created_at', 'updated_at']
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