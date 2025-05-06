from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import CustomUserSerializer, WorkoutLogSerializer
from .models import WorkoutLog
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

import json
from .models import WorkoutLog, NutritionLog
from .serializers import WorkoutLogSerializer, NutritionLogSerializer

# Sign-Up API View
@api_view(['POST'])
@permission_classes([AllowAny])
def signup_api(request):
    if request.method == 'POST':
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            return Response({
                'refresh': str(refresh),
                'access': str(access_token),
                'message': 'Account created successfully!',
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# In views.py
@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Set first_login_date if it's not set yet
            if not hasattr(user, 'first_login_date') or user.first_login_date is None:
                user.first_login_date = timezone.now()
                user.save()
                
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            return Response({
                'refresh': str(refresh),
                'access': str(access_token),
                'message': 'Login successful!',
                'first_login_date': user.first_login_date,
            }, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

# User Profile API View (Includes Workout Logs)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def profile_api(request):
    user = request.user
    
    # Get workout logs
    workout_logs = WorkoutLog.objects.filter(user=user)
    workout_logs_serializer = WorkoutLogSerializer(workout_logs, many=True)
    
    # Count nutrition logs
    nutrition_logs_count = NutritionLog.objects.filter(user=user).count()
    
    # Count workout logs
    workout_logs_count = workout_logs.count()
    
    user_data = {
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'date_of_birth': user.date_of_birth,
        'weight': user.weight,
        'height': user.height,
        'age': user.age,
        'gender': user.gender,
        'activity_level': user.activity_level,
        'first_login_date': user.first_login_date,
        'workout_logs': workout_logs_serializer.data,
        'workout_logs_count': workout_logs_count,
        'nutrition_logs_count': nutrition_logs_count,
    }
    return Response(user_data, status=status.HTTP_200_OK)

# Create & List Workout Logs
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def workout_logs_api(request):
    if request.method == 'GET':
        logs = WorkoutLog.objects.filter(user=request.user)
        serializer = WorkoutLogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        data = request.data.copy()
        data['user'] = request.user.id  # Set user ID to the logged-in user

        # Log the incoming data for debugging
        print("Received data:", json.dumps(data, indent=4))  # Log incoming data for debugging
        
        serializer = WorkoutLogSerializer(data=data)

        if serializer.is_valid():
            serializer.save(user=request.user)  # Save workout log with user association
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Log the serializer validation errors if any
            print("Serializer validation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def workout_log_detail_api(request, id):
    try:
        workout_log = WorkoutLog.objects.get(id=id, user=request.user)
    except WorkoutLog.DoesNotExist:
        return Response({'error': 'Workout log not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        workout_log.delete()
        return Response({'message': 'Workout log deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
    
# views.py
import requests
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def search_food_api(request):
    query = request.GET.get('query', '')
    if not query:
        return Response({'error': 'Query parameter is required'}, 
                       status=status.HTTP_400_BAD_REQUEST)

    headers = {'X-Api-Key': settings.CALORIE_NINJA_API_KEY}
    api_url = 'https://api.calorieninjas.com/v1/nutrition'
    
    try:
        response = requests.get(f'{api_url}?query={query}', headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Add a source field to distinguish API results
        for item in data.get('items', []):
            item['source'] = 'api'
            
        return Response(data, status=status.HTTP_200_OK)
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def nutrition_logs_api(request):
    if request.method == 'GET':
        try:
            logs = NutritionLog.objects.filter(user=request.user).order_by('-date_logged')
            serializer = NutritionLogSerializer(logs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error fetching nutrition logs: {str(e)}")  # Add logging
            return Response({'error': 'Failed to fetch nutrition logs'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'POST':
        try:
            data = request.data.copy()
            print(f"Received nutrition log data: {data}")  # Add logging
            
            serializer = NutritionLogSerializer(data=data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                print(f"Serializer errors: {serializer.errors}")  # Add logging
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error creating nutrition log: {str(e)}")  # Add logging
            return Response({'error': 'Failed to create nutrition log'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def nutrition_log_detail_api(request, id):
    try:
        nutrition_log = NutritionLog.objects.get(id=id, user=request.user)
    except NutritionLog.DoesNotExist:
        return Response({'error': 'Nutrition log not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        nutrition_log.delete()
        return Response({'message': 'Nutrition log deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    


@api_view(['PATCH'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_profile_api(request):
    user = request.user
    
    try:
        # Only update specified fields
        if 'weight' in request.data:
            user.weight = request.data['weight']
        if 'height' in request.data:
            user.height = request.data['height']
        if 'age' in request.data:
            user.age = request.data['age']
        if 'gender' in request.data:
            user.gender = request.data['gender']
        if 'activity_level' in request.data:
            user.activity_level = request.data['activity_level']
            
        user.save()
        
        serializer = CustomUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

from .models import Goal
from .serializers import GoalSerializer
from django.utils import timezone

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def goals_api(request):
    if request.method == 'GET':
        goals = Goal.objects.filter(user=request.user).order_by('-date_created')
        serializer = GoalSerializer(goals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        data = request.data.copy()
        serializer = GoalSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def goal_detail_api(request, id):
    try:
        goal = Goal.objects.get(id=id, user=request.user)
    except Goal.DoesNotExist:
        return Response({'error': 'Goal not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = GoalSerializer(goal)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        # If marking as complete, set completion date
        if request.data.get('is_completed') and not goal.is_completed:
            request.data['completion_date'] = timezone.now()
        
        serializer = GoalSerializer(goal, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        goal.delete()
        return Response({'message': 'Goal deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    

from .models import MindfulnessLog
from .serializers import MindfulnessLogSerializer

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def mindfulness_logs_api(request):
    if request.method == 'GET':
        logs = MindfulnessLog.objects.filter(user=request.user).order_by('-date_logged')
        serializer = MindfulnessLogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        data = request.data.copy()
        serializer = MindfulnessLogSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def mindfulness_log_detail_api(request, id):
    try:
        mindfulness_log = MindfulnessLog.objects.get(id=id, user=request.user)
    except MindfulnessLog.DoesNotExist:
        return Response({'error': 'Mindfulness log not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        mindfulness_log.delete()
        return Response({'message': 'Mindfulness log deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    



@api_view(['PATCH'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_account_api(request):
    """
    API endpoint to update user account information (email and password)
    """
    user = request.user
    data = request.data
    response_data = {}
    status_code = status.HTTP_200_OK
    
    try:
        # Update email if provided
        if 'email' in data:
            # Validate email format
            if '@' not in data['email']:
                return Response(
                    {'error': 'Please provide a valid email address.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if email is already in use by another user
            if get_user_model().objects.filter(email=data['email']).exclude(id=user.id).exists():
                return Response(
                    {'error': 'This email is already in use.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.email = data['email']
            response_data['email'] = data['email']
        
        # Update password if provided
        if 'new_password' in data:
            if not data.get('current_password'):
                return Response(
                    {'error': 'Current password is required to set a new password.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verify current password
            if not user.check_password(data['current_password']):
                return Response(
                    {'error': 'Current password is incorrect.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(data['new_password'])
            response_data['password_updated'] = True
            
            # Generate new token since password change invalidates existing tokens
            refresh = RefreshToken.for_user(user)
            response_data['refresh'] = str(refresh)
            response_data['access'] = str(refresh.access_token)
        
        user.save()
        response_data['message'] = 'Account updated successfully'
        
        return Response(response_data, status=status_code)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )