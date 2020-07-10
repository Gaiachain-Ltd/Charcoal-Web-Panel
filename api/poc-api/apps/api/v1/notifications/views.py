from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.notifications.models import Notification
from config.swagger_schema import CustomSchema

from .serializers import NotificationSerializer


class NotificationViewSet(ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    schema = CustomSchema()

    def get_queryset(self):
        user = self.request.user
        queryset = Notification.objects.filter(users=user).exclude(read_by=user)
        user.read_notifications.add(*queryset)
        return queryset
