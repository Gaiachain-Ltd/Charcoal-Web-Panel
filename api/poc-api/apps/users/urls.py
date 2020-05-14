from django.urls import path

from rest_framework_simplejwt import views as jwt_views
from apps.users.views import RegistrationAPIView, RoleListAPIView, UserListAPIView, TokenObtainPairView

app_name = 'users'

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='login-view'),
    path('token-refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    # Registration endpoint not needed now
    path('register/', RegistrationAPIView.as_view(), name='register'),
    path('roles/', RoleListAPIView.as_view(), name='roles'),
    path('agents/', UserListAPIView.as_view(), name='agents'),
]
