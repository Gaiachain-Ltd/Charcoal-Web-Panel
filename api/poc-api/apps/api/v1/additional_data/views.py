from rest_framework import status
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, ErrorDetail

from apps.additional_data.models import Village, Destination,  Parcel, TreeSpecie, OvenType
from apps.api.v1.additional_data.serializers import (
    VillageSerializer, DestinationSerializer, ParcelSerializer, TreeSpecieSerializer, OvenTypeSerializer
)
from config.swagger_schema import CustomSchema


class BaseAdditionalDataViewSet(object):
    schema = CustomSchema()
    filter_backends = (SearchFilter,)

    def get_queryset(self):
        return self.model.objects.filter(active=True)

    def perform_destroy(self, instance):
        instance.active = False
        instance.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        if serializer.errors:
            if 'name' in serializer.errors:
                name_errors = serializer.errors['name']
                if len(name_errors) == 1 and name_errors[0].code == 'unique':
                    objects = self.model.objects.filter(name=request.data['name'], active=False)
                    if objects.count():
                        objects.update(active=True)
                        raise ValidationError({
                            'name': [ErrorDetail(
                                f'{str(name_errors[0])} Object is set active again. Refresh the page to see the change.',
                                name_errors[0].code
                            )]
                        })
                    raise ValidationError(serializer.errors)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class AdditionalDataViewSet(BaseAdditionalDataViewSet, ViewSet):
    """
    Viewset with additional data
    """
    search_fields = ('name',)

    @action(methods=['get'], detail=False, filter_backends=(SearchFilter,), search_fields=('name',))
    def all_data(self, request):
        data = {
            'villages': VillageSerializer(Village.objects.filter(active=True), many=True).data,
            'parcels': ParcelSerializer(Parcel.objects.filter(active=True), many=True).data,
            'destinations': DestinationSerializer(Destination.objects.filter(active=True), many=True).data,
            'tree_species': TreeSpecieSerializer(TreeSpecie.objects.filter(active=True), many=True).data,
            'oven_types': OvenTypeSerializer(OvenType.objects.filter(active=True), many=True).data,
        }
        return Response(data)


class ParcelViewSet(BaseAdditionalDataViewSet, ModelViewSet):
    serializer_class = ParcelSerializer
    model = Parcel

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        if self.action == 'unused':
            queryset = queryset.filter(parcel_loggings__isnull=True)
        return queryset

    @action(methods=['get'], detail=False)
    def unused(self, request):
        return self.list(request)


class VillageViewSet(BaseAdditionalDataViewSet, ModelViewSet):
    serializer_class = VillageSerializer
    model = Village


class DestinationViewSet(BaseAdditionalDataViewSet, ModelViewSet):
    serializer_class = DestinationSerializer
    model = Destination


class TreeSpecieViewSet(BaseAdditionalDataViewSet, ModelViewSet):
    serializer_class = TreeSpecieSerializer
    model = TreeSpecie


class OvenTypeViewSet(BaseAdditionalDataViewSet, ModelViewSet):
    serializer_class = OvenTypeSerializer
    model = OvenType
