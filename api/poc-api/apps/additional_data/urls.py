from rest_framework.routers import DefaultRouter

from apps.additional_data.views import (
    AdditionalDataViewSet
)

app_name = 'additional_data'

router = DefaultRouter()
router.register('', AdditionalDataViewSet, base_name='additional-data')

urlpatterns = router.urls
