from django.contrib import admin
from django.urls import path, include
from momentum import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('momentum/', include('momentum.urls')),  # Make sure momentum app URLs are included
]
