from rest_framework.routers import DefaultRouter

from .views import NotificationViewSet

app_name = 'entities'

router = DefaultRouter()
router.register('', NotificationViewSet, base_name='notifications')

urlpatterns = router.urls
