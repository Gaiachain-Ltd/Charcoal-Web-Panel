from rest_framework.routers import DefaultRouter

from apps.api.v1.entities.views import (
    EntityViewSet, RelationsViewSet, PackageViewSet, ReplantationViewSet
)

app_name = ''

router = DefaultRouter()
router.register('', EntityViewSet, base_name='entities')
router.register('packages', PackageViewSet, base_name='packages')
router.register('relations', RelationsViewSet, base_name='relations')
router.register('replantation', ReplantationViewSet, base_name='replantation')

urlpatterns = router.urls
