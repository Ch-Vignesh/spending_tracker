# urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Login and Logout Views
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),  # Logs out and redirects to login page
    
    # Include tracker URLs
    path('', include('tracker.urls')),  
]
