from rest_framework.routers import DefaultRouter

from apps.api.v1.entities.views import (
    EntityViewSet, PackageViewSet, ReplantationViewSet
)

app_name = 'entities'

router = DefaultRouter()
router.register('', EntityViewSet, base_name='entities')
router.register('packages', PackageViewSet, base_name='packages')
router.register('replantation', ReplantationViewSet, base_name='replantation')

urlpatterns = router.urls
