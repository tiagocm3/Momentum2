from django.contrib import admin
from django.urls import path, include  # Import include to include app URLs
from django.http import HttpResponse  # Import for a simple placeholder view

# Placeholder view for the root URL
def home(request):
    return HttpResponse("Welcome to Momentum Backend!")

urlpatterns = [
    path('', home, name='home'),  # Root URL that serves as the homepage
    path('admin/', admin.site.urls),  # Admin site
    path('api/', include('core.urls')),  # Include the core app's URLs under '/api/'
]
