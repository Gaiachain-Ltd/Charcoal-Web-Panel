from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from rest_framework_simplejwt.views import TokenObtainPairView as CoreTokenObtainPairView

from apps.users.serializers import RegistrationSerializer, RoleSerializer, UserSerializer, TokenObtainPairSerializer
from apps.users.models import Role

User = get_user_model()


class PingAPIView(APIView):
    """
    Endpoint for checking connection with server. Returns 200 status and "OK".
    """
    def get(self, request, format=None):
        return Response("OK", status=status.HTTP_200_OK)


class RoleListAPIView(ListAPIView):
    """
    List of existing roles
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class UserListAPIView(ListAPIView):
    """
    List of existing agents
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RegistrationAPIView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TokenObtainPairView(CoreTokenObtainPairView):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    serializer_class = TokenObtainPairSerializer
