from rest_framework.viewsets import ViewSet
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps.additional_data.models import Village, Destination,  Parcel, TreeSpecie, OvenType
from apps.additional_data.serializers import (
    VillageSerializer, DestinationSerializer, ParcelSerializer, TreeSpecieSerializer, OvenTypeSerializer
)


class AdditionalDataViewSet(ViewSet):
    """
    Viewset with additional data
    """
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    permission_classes = [AllowAny]

    @action(methods=['get'], detail=False, filter_backends=(SearchFilter,), search_fields=('name',))
    def villages(self, request):
        queryset = Village.objects.all()
        serializer = VillageSerializer(queryset, many=True)
        data = {
            'count': len(serializer.data),
            'results': serializer.data
        }
        return Response(data)

    @action(methods=['get'], detail=False, filter_backends=(SearchFilter,), search_fields=('name',))
    def parcels(self, request):
        queryset = Parcel.objects.all()
        serializer = ParcelSerializer(queryset, many=True)
        data = {
            'count': len(serializer.data),
            'results': serializer.data
        }
        return Response(data)

    @action(methods=['get'], detail=False, filter_backends=(SearchFilter,), search_fields=('name',))
    def destinations(self, request):
        queryset = Destination.objects.all()
        serializer = DestinationSerializer(queryset, many=True)
        data = {
            'count': len(serializer.data),
            'results': serializer.data
        }
        return Response(data)

    @action(methods=['get'], detail=False, filter_backends=(SearchFilter,), search_fields=('name',))
    def tree_species(self, request):
        queryset = TreeSpecie.objects.all()
        serializer = TreeSpecieSerializer(queryset, many=True)
        data = {
            'count': len(serializer.data),
            'results': serializer.data
        }
        return Response(data)

    @action(methods=['get'], detail=False, filter_backends=(SearchFilter,), search_fields=('name',))
    def oven_types(self, request):
        queryset = OvenType.objects.all()
        serializer = OvenTypeSerializer(queryset, many=True)
        data = {
            'count': len(serializer.data),
            'results': serializer.data
        }
        return Response(data)

    @action(methods=['get'], detail=False, filter_backends=(SearchFilter,), search_fields=('name',))
    def all_data(self, request):
        data = {
            'villages': VillageSerializer(Village.objects.all(), many=True).data,
            'parcels': ParcelSerializer(Parcel.objects.all(), many=True).data,
            'destinations': DestinationSerializer(Destination.objects.all(), many=True).data,
            'tree_species': TreeSpecieSerializer(TreeSpecie.objects.all(), many=True).data,
            'oven_types': OvenTypeSerializer(OvenType.objects.all(), many=True).data,
        }
        return Response(data)
