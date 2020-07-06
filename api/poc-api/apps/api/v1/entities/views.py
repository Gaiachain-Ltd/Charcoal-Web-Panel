import json
import pytz
from datetime import datetime

from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.entities.models import Entity,  Package, Oven, Replantation
from apps.api.v1.entities.serializers import (
    EntitySerializer, PackagePidSerializer, EntityListSerializer,
    PackagesSerializer, PackageDetailsSerializer, OvenSimpleSerializer, ReplantationSerializer,
    ReplantationListSerializer
)
from apps.api.v1.additional_data.mixins import MultiSerializerMixin
from apps.api.v1.entities.pagination import LimitOffsetPagination
from config.swagger_schema import CustomSchema


class EntityViewSet(ViewSet, MultiSerializerMixin):
    """
    Viewset for entities
    """
    lookup_field = 'pk'
    queryset = Entity.objects.all()
    pagination_class = LimitOffsetPagination
    schema = CustomSchema()
    serializer_class = EntityListSerializer
    custom_serializer_classes = {
        'new': EntitySerializer,
        'harvests': PackagePidSerializer,
    }

    @action(methods=['get'], detail=False)
    def types(self, request):
        """
        ---
        desc: GET endpoint for list of possible actions
        ret: dict with actions. Key - short name, Value - full name.
        ---
        """
        return Response({i[0]: i[1] for i in Entity.ACTIONS}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def new(self, request, pk=None):
        """
        ---
        desc: POST for creating new action
        ret: package pid
        input:
        -
            name: action
            required: true
            location: form
            type: string
        -
            name: pid
            required: false
            location: form
            type: string
        -
            name: timestamp
            required: true
            location: form
            type: integer
        -
            name: properties
            required: true
            location: form
            type: object
        -
            name: documents_photos/receipt_photos
            required: false
            location: form
            type: image
        -
            name: location
            required: true
            location: form
            type: object
        ---
        """
        ser = self.get_serializer(data=request.data, context={'request': request})
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response({
            'pid': ser.instance.package.pid,
            'package_id': ser.instance.package_id,
            'timestamp': ser.instance.timestamp
        }, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def plots(self, request):
        """
        ---
        desc: List API plots with defined action code
        ret: List of plot actions
        input:
        -
            name: last_action
            required: true
            location: query
            type: string
        ---
        """
        last_action = request.GET.get('last_action')
        queryset = Package.objects.filter(
            type=Package.PLOT,
            package_entities__user=request.user,
            last_action__action=last_action,
            plot_harvest__isnull=True
        ).distinct()
        page = self.paginator.paginate_queryset(queryset=queryset, request=request)
        if page is not None:
            serializer = PackagePidSerializer(page, many=True)
            return self.paginator.get_paginated_response(serializer.data)
        serializer = PackagePidSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def harvests(self, request):
        """
        ---
        desc: List API harvests with defined action code
        ret: List of harvests actions
        input:
        -
            name: last_action
            required: true
            location: query
            type: string
        ---
        """
        last_action = request.GET.get('last_action')
        queryset = Package.objects.filter(
            type=Package.HARVEST,
            package_entities__user=request.user,
            last_action__action=last_action
        ).distinct()
        page = self.paginator.paginate_queryset(queryset=queryset, request=request)
        if page is not None:
            serializer = PackagePidSerializer(page, many=True)
            return self.paginator.get_paginated_response(serializer.data)
        serializer = PackagePidSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def ovens(self, request):
        """
        ---
        desc: List API active ovens for given harvest
        ret: List of ovens
        input:
        -
            name: harvest_id
            required: true
            location: query
            type: string
        ---
        """
        harvest_id = request.GET.get('harvest_id')
        queryset = Oven.objects.filter(
            carbonization_beginning__entity__package_id=harvest_id,
            carbonization_beginning__entity__user=request.user,
            carbonization_ending__isnull=True
        ).distinct()
        page = self.paginator.paginate_queryset(queryset=queryset, request=request)
        if page is not None:
            serializer = OvenSimpleSerializer(page, many=True)
            return self.paginator.get_paginated_response(serializer.data)
        serializer = OvenSimpleSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def _filter_entities(self, request, additional_filters={}):
        from_timestamp = request.GET.get('from_timestamp')
        to_timestamp = request.GET.get('to_timestamp')

        filter_kwargs = {}
        if from_timestamp and to_timestamp:
            filter_kwargs['timestamp__range'] = (from_timestamp, to_timestamp)
        elif from_timestamp and not to_timestamp:
            filter_kwargs['timestamp__gte'] = from_timestamp
        elif to_timestamp and not from_timestamp:
            filter_kwargs['timestamp__lte'] = to_timestamp
        if request and 'keyword' in request.query_params and len(request.query_params['keyword']) > 0:
            filter_kwargs['package__pid__icontains'] = request.query_params['keyword']
        if request and 'types' in request.query_params and len(request.query_params['types']) > 0:
            filter_kwargs['package__type__in'] = [t.upper() for t in request.query_params['types'].split(',')]
        filter_kwargs = {**filter_kwargs, **additional_filters}

        return filter_kwargs

    def list(self, request, *args, **kwargs):
        """
        ---
        desc: List API for actions.
        ret: List of entities with pids and action types only
        input:
        -
            name: from_timestamp
            required: false
            location: query
            type: integer
        -
            name: to_timestamp
            required: false
            location: query
            type: integer
        -
            name: keyword
            required: false
            location: query
        -
            name: limit
            required: false
            location: query
            type: integer
        -
            name: offset
            required: false
            location: query
            type: integer
        """
        filter_kwargs = self._filter_entities(request)
        entities = self.queryset.filter(**filter_kwargs)
        ser = self.serializer_class(entities, many=True)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset=ser.data, request=request)
        if page is not None:
            return paginator.get_paginated_response(page)
        return Response(ser.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def dots(self, request):
        dates = json.loads(request.query_params.get('dates', None))
        response = {}
        for timestamp in dates:
            start_timestamp = int(timestamp)
            end_timestamp = start_timestamp + 24 * 60 * 60 - 1  # -1 to cover midnight edgecase
            available_actions = list(
                Package.objects.filter(
                    package_entities__timestamp__range=(start_timestamp, end_timestamp)
                ).values_list('type').distinct()
            )
            response[start_timestamp] = available_actions
        return Response(response, status=status.HTTP_200_OK)


class PackageViewSet(ViewSet, MultiSerializerMixin):
    """
    Viewset for packages
    """
    lookup_field = 'pk'
    queryset = Package.objects.order_by('-id')
    pagination_class = LimitOffsetPagination
    schema = CustomSchema()
    serializer_class = PackagesSerializer
    custom_serializer_classes = {
        'get_package_details': PackageDetailsSerializer,
    }

    def _filter_entities(self, request, additional_filters={}):
        from_timestamp = request.GET.get('from_timestamp')
        to_timestamp = request.GET.get('to_timestamp')

        filter_kwargs = {}
        if from_timestamp and to_timestamp:
            filter_kwargs['package_entities__timestamp__range'] = (from_timestamp, to_timestamp)
        elif from_timestamp and not to_timestamp:
            filter_kwargs['package_entities__timestamp__gte'] = from_timestamp
        elif to_timestamp and not from_timestamp:
            filter_kwargs['package_entities__timestamp__lte'] = to_timestamp
        if request and 'keyword' in request.query_params and len(request.query_params['keyword']) > 0:
            filter_kwargs['pid__icontains'] = request.query_params['keyword']

        filter_kwargs = {**filter_kwargs, **additional_filters}

        return filter_kwargs

    def list(self, request):
        """
        ---
        desc: List API for packages
        ret: List of packages
        input:
        -
            name: type
            required: false
            location: query
            type: string
        ---
        """
        type = request.GET.get('type')
        filter_kwargs = self._filter_entities(request)
        if type and type.lower() != 'all':
            filter_kwargs['type'] = type.upper()
        queryset = self.queryset.filter(
            **filter_kwargs
        ).exclude(last_action__action=Entity.INITIAL).distinct()
        page = self.paginator.paginate_queryset(queryset=queryset, request=request)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.paginator.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True)
    def get_package_details(self, request, pk=None):
        """
        ---
        desc: Details API for package
        ret: details for package by pk
        input:
        -
            name: id
            required: true
            location: path
            type: integer
        ---
        """
        package = get_object_or_404(Package, pk=pk)
        serializer = self.get_serializer(package)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_package_chain_queryset(self, pk):
        package = get_object_or_404(Package, pk=pk)
        return self.queryset.filter(
            Q(id=package.id) |  # matches self
            Q(plot=package) |  # matches harvest's plot
            Q(harvest=package) |  # matches truck's harvest
            Q(trucks=package) |  # matches harvest's trucks
            Q(plot_harvest=package) |  # matches plot's harvest
            Q(plot_harvest__trucks=package) |  # matches plot's trucks
            Q(harvest__plot=package) |  # matches truck's plot
            Q(harvest__trucks=package)  # matches truck's other trucks
        ).distinct().order_by('id')

    @action(methods=['get'], detail=True)
    def get_package_chain(self, request, pk=None):
        """
        ---
        desc: Chain of actions for package
        ret: Chain of actions for package
        input:
        -
            name: id
            required: true
            location: path
            type: integer
        ---
        """
        chain = self.get_serializer(self.get_package_chain_queryset(pk), many=True)
        return Response(chain.data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def finalize_supply_chain(self, request, pk=None):
        """
        ---
        desc: Mark supply chain as complete
        ret: Chain of actions for package
        input:
        -
            name: id
            required: true
            location: path
            type: integer
        ---
        """
        queryset = self.get_package_chain_queryset(pk)
        queryset.update(is_finished=True)
        chain = self.get_serializer(self.get_package_chain_queryset(pk), many=True)
        return Response(chain.data, status=status.HTTP_200_OK)


class ReplantationViewSet(mixins.CreateModelMixin,
                          mixins.ListModelMixin,
                          GenericViewSet):
    """
        Viewset API for Replantations
    """

    queryset = Replantation.objects.all().order_by('-id')
    pagination_class = LimitOffsetPagination
    schema = CustomSchema()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_serializer_class(self):
        if self.action == 'list':
            return ReplantationListSerializer
        return ReplantationSerializer

    def translate_year_to_timestamp_range(self, year):
        year_date = pytz.timezone(settings.TIME_ZONE).localize(datetime.strptime(str(year), '%Y'))
        return year_date.timestamp(), year_date.replace(month=12, day=31).timestamp()

    def _filter_entities(self, request):
        year = request.GET.get('year')

        filter_q = Q()
        if year:
            from_timestamp, to_timestamp = self.translate_year_to_timestamp_range(year)
            filter_q |= Q(beginning_date__range=(from_timestamp, to_timestamp)) | \
                        Q(ending_date__range=(from_timestamp, to_timestamp))

        return filter_q

    def list(self, request, *args, **kwargs):
        """
        ---
        desc: List API for replantations
        ret: List of replantations
        input:
        -
            name: year
            required: false
            location: query
            type: number
        ---
        """
        filter_q = self._filter_entities(request)
        queryset = self.queryset.filter(filter_q).distinct()
        page = self.paginator.paginate_queryset(queryset=queryset, request=request)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.paginator.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def plots(self, request):
        """
        ---
        desc: List API for Packages without replantation and with Logging Ending step.
        ret: List of packages
        ---
        """
        queryset = Package.objects.filter(type=Package.PLOT, last_action__action=Entity.LOGGING_ENDING, replantation__isnull=True).distinct()
        page = self.paginator.paginate_queryset(queryset=queryset, request=request)
        if page is not None:
            serializer = PackagePidSerializer(page, many=True)
            return self.paginator.get_paginated_response(serializer.data)
        serializer = PackagePidSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
