from django.urls import path

from rest_framework_simplejwt import views as jwt_views
from apps.api.v1.users.views import RegistrationAPIView, RoleListAPIView, UserListAPIView, TokenObtainPairView
from config.swagger_schema import CustomSchema

app_name = 'users'

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='login-view'),
    path('token-refresh/', jwt_views.TokenRefreshView.as_view(**{'schema': CustomSchema()}), name='token_refresh'),
    path('register/', RegistrationAPIView.as_view(), name='register'),
    path('roles/', RoleListAPIView.as_view(), name='roles'),
    path('agents/', UserListAPIView.as_view(), name='agents'),
]
