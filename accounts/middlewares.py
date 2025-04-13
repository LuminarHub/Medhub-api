# Create a new file middleware.py in your app directory

from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class HospitalAdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before the view is called
        
        # Check if the request path starts with hospital-admin
        if request.path.startswith('/hospital-admin/'):
            # If user is authenticated
            if request.user.is_authenticated:
                # If user is a superuser, allow access
                if request.user.is_superuser:
                    pass
                # If user is a Doctor with staff status, allow access
                elif hasattr(request.user, 'doctor') and request.user.is_staff:
                    pass
                # If user has a related hospital, allow access
                elif hasattr(request.user, 'hospital_set') and request.user.hospital_set.exists() and request.user.is_staff:
                    pass
                # Otherwise, redirect to admin login
                else:
                    messages.error(request, "You don't have permission to access the hospital admin site.")
                    return redirect(reverse('admin:login'))
        
        response = self.get_response(request)
        return response