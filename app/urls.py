from django.urls import path
from .views import LoginAPIView, SignupAPIView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('api/login/', LoginAPIView.as_view(), name='login_api'),
    path('api/signup/', SignupAPIView.as_view(), name='signup_api'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # ... other URL patterns
]