from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as CoreTokenObtainPairSerializer

from apps.users.models import Role

User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('name', 'id')


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'role')

    def get_role(self, obj):
        if obj.is_superuser:
            return {
                "name": "SUPER_USER",
                "id": None
            }
        return RoleSerializer(instance=obj.role).data


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'token', 'role', 'first_name', 'last_name', 'function', 'contact')

    @transaction.atomic
    def create(self, validated_data):
        # FIXME:
        if self.context['user'].is_superuser and validated_data['role'].name == 'SUPER_USER':
            validated_data['is_superuser'] = True
            validated_data['is_staff'] = True
        user = User.objects.create_user(**validated_data)
        user.add_to_chain()
        return user


class TokenObtainPairSerializer(CoreTokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data = {
            'email': self.user.email,
            'role': RoleSerializer(instance=self.user.role).data,
            'full_name': self.user.get_full_name(),
            'contact': self.user.contact,
            'code': self.user.code,
            'function': self.user.get_function_display(),
            **data
        }
        return data