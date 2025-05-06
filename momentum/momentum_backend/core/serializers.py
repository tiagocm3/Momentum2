from rest_framework import serializers
from .models import CustomUser  # Import your actual model

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser  # ✅ Use CustomUser instead of User
        fields = ['email', 'password', 'first_name', 'last_name', 'date_of_birth']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            date_of_birth=validated_data.get('date_of_birth', None)
        )
        return user

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'date_of_birth']