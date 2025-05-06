from django.contrib import admin
from django.contrib.auth.models import User

# If you've already registered the User model, you can unregister it before doing any custom registration
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

# Now, you can register a custom User model (if applicable) or customize it
from .models import CustomUser  # If you're using a custom user model

# CustomAdmin class for CustomUser
class CustomUserAdmin(admin.ModelAdmin):
    # Fields to display in the admin panel
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined')
    
    # Fields to search by in the admin panel
    search_fields = ('email', 'first_name', 'last_name')
    
    # Add filters to the sidebar for filtering the users
    list_filter = ('is_active', 'is_staff', 'date_joined')
    
    # Set the default ordering for users in the admin panel
    ordering = ('-date_joined',)

# Register the CustomUser model with the custom admin class
admin.site.register(CustomUser, CustomUserAdmin)
