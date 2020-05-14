from rest_framework.routers import DefaultRouter

from apps.entities.views import (
    EntityViewSet, RelationsViewSet, PackageViewSet
)

app_name = ''

router = DefaultRouter()
router.register('', EntityViewSet, base_name='entities')
router.register('packages', PackageViewSet, base_name='packages')
router.register('relations', RelationsViewSet, base_name='relations')

urlpatterns = router.urls
