Health & Fitness Tracker
A comprehensive health and fitness tracking application built with React Native for iOS frontend and Django REST framework for the backend.
📱 Features

User Authentication: Secure login and registration system
Workout Tracking: Log and monitor your exercise activities
Nutrition Logging: Track your food intake and calories
Goal Setting: Set and track fitness and health goals
Mental Health: Mindfulness logs and mental wellness advice
Progress Visualization: View your fitness journey through charts and statistics

🛠️ Tech Stack
Frontend

React Native - Cross-platform mobile framework
React Navigation - Navigation library for React Native apps
AsyncStorage - Local data storage
React Native Vector Icons - Icon library
React Native Community Components - DateTimePicker, Slider
Animated API - For smooth animations and transitions

Backend

Django - Python web framework
Django REST Framework - API toolkit for Django
Simple JWT - JWT authentication for Django REST Framework
SQLLite

🏗️ Project Structure
Frontend Components

Authentication screens (Login, Register)
Dashboard and summary screens
Workout logging interface
Nutrition tracking system
Goal setting and tracking
Settings and user profile management
Mental health and mindfulness components

Backend Structure

Custom User model extending AbstractUser
Models for WorkoutLog, NutritionLog, Goal, MindfulnessLog
JWT authentication system
REST API endpoints for all features
Admin interface customization

🚀 Getting Started
Prerequisites

Node.js (v14 or higher)
Python (v3.8 or higher)
Xcode (for iOS development)
pip (Python package manager)
npm or yarn

Backend Setup

Clone the repository https://github.com/tiagocm3/Momentum2
git clone 


Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies
pip install -r requirements.txt

Run migrations
python manage.py migrate

Create a superuser (admin)
python manage.py createsuperuser

Start the development server
python manage.py runserver

Frontend Setup

Navigate to the frontend directory
cd ../frontend

Install dependencies
npm install
# or
yarn install

Start the Metro server
npx react-native start

Run the app on iOS
npx react-native run-ios










