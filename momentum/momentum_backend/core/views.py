from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomUserSerializer  # Ensure you have a serializer for CustomUser
from .models import CustomUser  # If using a CustomUser model

# Sign Up View
class SignUpView(APIView):
    def post(self, request):
        print("Received data:", request.data)
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        else:
            print("Serializer errors:", serializer.errors)  # Debugging: See what's wrong
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Login View
class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

# Profile View (For viewing user profile)
class ProfileView(APIView):
    def get(self, request):
        # Fetching the logged-in user's information
        user = request.user
        if user.is_authenticated:
            # You can return the profile data in a customized response or render a template
            return Response({
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "date_of_birth": user.date_of_birth,
                # Add any other fields you need from your CustomUser model
            })
        return Response({"message": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

# Update Profile View (For editing user profile)
class UpdateProfileView(APIView):
    def put(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"message": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Retrieve the data sent in the request to update the user information
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        date_of_birth = request.data.get('date_of_birth')

        # Update the user instance
        user.first_name = first_name
        user.last_name = last_name
        user.date_of_birth = date_of_birth
        user.save()

        return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)

