from django.urls import path
from .views import LoginAPIView

urlpatterns = [
    path('api/login/', LoginAPIView.as_view(), name='login_api'),
    # ... other URL patterns
]