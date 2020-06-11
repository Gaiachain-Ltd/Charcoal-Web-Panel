from rest_framework.routers import DefaultRouter

from apps.additional_data.views import (
    AdditionalDataViewSet, ParcelViewSet, VillageViewSet, DestinationViewSet, TreeSpecieViewSet, OvenTypeViewSet
)

app_name = 'additional_data'

router = DefaultRouter()
router.register('', AdditionalDataViewSet, base_name='additional-data')
router.register('parcels', ParcelViewSet, base_name='parcels')
router.register('villages', VillageViewSet, base_name='villages')
router.register('destinations', DestinationViewSet, base_name='destinations')
router.register('tree-species', TreeSpecieViewSet, base_name='tree-species')
router.register('oven-types', OvenTypeViewSet, base_name='oven-types')

urlpatterns = router.urls
