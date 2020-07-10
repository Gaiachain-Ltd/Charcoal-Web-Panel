from rest_framework import serializers
from rest_framework.exceptions import NotFound

from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    package_pid = serializers.CharField(source='package.pid')

    class Meta:
        model = Notification
        fields = ('package_pid', 'action_name')
