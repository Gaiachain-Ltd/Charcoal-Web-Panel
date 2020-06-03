import json

from django.utils import timezone
from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from apps.entities.models import Entity,  Package, Oven
from apps.entities.serializers import (
    EntitySerializer, PackagePidSerializer, EntityListSerializer, EntityBatchSerializer, EntityBatchListSerializer,
    PackagesSerializer, PackageDetailsSerializer, ChainSeriazlier, OvenSimpleSerializer
)
from apps.additional_data.mixins import MultiSerializerMixin
from apps.entities.utils import unix_to_datetime_tz
from apps.entities.pagination import LimitOffsetPagination
from config.swagger_schema import CustomSchema


class EntityViewSet(ViewSet, MultiSerializerMixin):
    """
    Viewset for entities
    """
    lookup_field = 'pk'
    queryset = Entity.objects.all()
    pagination_class = LimitOffsetPagination
    schema = CustomSchema()
    permission_classes = [AllowAny]
    serializer_class = EntityListSerializer
    custom_serializer_classes = {
        'new': EntitySerializer,
        'harvests': PackagePidSerializer,
        'batch': EntityBatchSerializer,
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

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
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
        return Response({'pid': ser.instance.package.pid}, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
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
            last_action__action=last_action
        ).distinct()
        page = self.paginator.paginate_queryset(queryset=queryset, request=request)
        if page is not None:
            serializer = PackagePidSerializer(page, many=True)
            return self.paginator.get_paginated_response(serializer.data)
        serializer = PackagePidSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
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

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def ovens(self, request):
        """
        ---
        desc: List API ovens for given harvest
        ret: List of ovens
        input:
        -
            name: harvest_pid
            required: true
            location: query
            type: string
        ---
        """
        harvest_pid = request.GET.get('harvest_pid')
        queryset = Oven.objects.filter(
            carbonization_beginning__entity__package__pid=harvest_pid,
            carbonization_beginning__entity__user=request.user,
            carbonization_endings__isnull=True
        ).distinct()
        page = self.paginator.paginate_queryset(queryset=queryset, request=request)
        if page is not None:
            serializer = OvenSimpleSerializer(page, many=True)
            return self.paginator.get_paginated_response(serializer.data)
        serializer = OvenSimpleSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, lookup_field='qr_code')
    def get_pid(self, request, pk=None):
        """
        ---
        desc: Details API for package
        ret: details for package by qr_code
        input:
        -
            name: qr_code
            required: true
            location: path
        ---
        """
        package = get_object_or_404(Package, qr_code=pk)
        return Response(package.pid, status=status.HTTP_200_OK)

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

    @action(methods=['post'], detail=False, serializer_class=EntityBatchSerializer)
    def batch(self, request):
        """
        ---
        desc: Batch list API for actions
        ret: List of entities with all details by list of pids
        input:
        -
            name: pids
            required: false
            location: body
            type: dict
        -
            name: from_timestamp
            required: false
            location: query
            type: integer
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
        additional_filters = {}
        if 'pids' in request.data:
            ser = self.serializer_class(data={'pids': request.data['pids']})
            ser.is_valid(raise_exception=True)
            additional_filters = {'package__pid__in': ser.validated_data['pids']} if ser.validated_data['pids'] else {}
        filter_kwargs = self._filter_entities(request, additional_filters=additional_filters)
        entities = self.queryset.filter(**filter_kwargs)
        ser = EntityBatchListSerializer(entities, many=True)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset=ser.data, request=request)
        if page is not None:
            return paginator.get_paginated_response(page)
        return Response(ser.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, serializer_class=EntityBatchSerializer)
    def batch_web(self, request):
        """
        ---
        desc: Batch list API for actions
        ret: List of entities with all details by list of pids
        input:
        -
            name: pids
            required: false
            location: body
            type: dict
        -
            name: from_timestamp
            required: false
            location: query
            type: integer
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
        entities = self.queryset.filter(**filter_kwargs).exclude(action=Entity.INITIAL)
        ser = EntityBatchListSerializer(entities, many=True)
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
            end_timestamp = int(start_timestamp) + 24 * 60 * 60
            available_actions = list(
                Package.objects.filter(
                    package_entities__timestamp__range=(start_timestamp, end_timestamp)
                ).values_list('type').distinct()
            )
            response[start_timestamp] = available_actions
        return Response(response, status=status.HTTP_200_OK)


class RelationsViewSet(ViewSet):
    """
    Viewset for relations between entities
    """
    pagination_class = LimitOffsetPagination
    serializer_class = EntityBatchSerializer
    schema = CustomSchema()
    permission_classes = [AllowAny]

    def _filter_entities(self, request, additional_filters={}):
        from_timestamp = unix_to_datetime_tz(request.GET.get('from_timestamp'))
        to_timestamp = unix_to_datetime_tz(request.GET.get('to_timestamp'))

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

    @action(methods=['post'], detail=False)
    def batch(self, request):
        """
        Batch of relations
        """
        ser = EntityBatchSerializer(data={'pids': request.data['pids']})
        ser.is_valid(raise_exception=True)
        additional_filters = {'pid__in': ser.validated_data['pids']} if ser.validated_data['pids'] else {}
        filter_kwargs = self._filter_entities(request, additional_filters=additional_filters)
        packages = Package.objects.filter(**filter_kwargs)
        response_data = []
        for p in packages:
            if p.type == Package.HARVEST:
                related_pids = [p.sac.pid] if p.sac else []
                response_data.append({
                    p.pid: related_pids
                })
            elif p.type == Package.SAC:
                related_pids = list(p.package_harvests.values_list('pid', flat=True))
                if p.lot:
                    related_pids.extend([p.lot.pid])
                response_data.append({
                    p.pid: related_pids
                })
            elif p.type == Package.LOT:
                response_data.append({
                    p.pid: list(p.package_sacs.values_list('pid', flat=True))
                })
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset=response_data, request=request)
        if page is not None:
            return paginator.get_paginated_response(page)
        return Response(response_data, status=status.HTTP_200_OK)


class PackageViewSet(ViewSet, MultiSerializerMixin):
    """
    Viewset for packages
    """
    lookup_field = 'pk'
    queryset = Package.objects.order_by('-id')
    pagination_class = LimitOffsetPagination
    schema = CustomSchema()
    permission_classes = [AllowAny]
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
        ).exclude(last_action__action=Entity.INITIAL)
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
        package = get_object_or_404(Package, pk=pk)
        chain = []

        # TODO Works, but looks ugly, need to refactor
        if package.type == Package.HARVEST:
            for entity in package.package_entities.all():
                chain.append(ChainSeriazlier(entity).data)
            if package.sac:
                chain.append(ChainSeriazlier(package.sac.package_entities.first()).data)
                if package.sac.lot:
                    for entity in package.sac.lot.package_entities.exclude(action=Entity.INITIAL):
                        chain.append(ChainSeriazlier(entity).data)
        elif package.type == Package.SAC:
            for harvest_entity in Entity.objects.filter(package__type=Package.HARVEST, package__sac=package):
                chain.append(ChainSeriazlier(harvest_entity).data)
            for entity in package.package_entities.all():
                chain.append(ChainSeriazlier(entity).data)
            if package.lot:
                lot_data = ChainSeriazlier(package.lot.package_entities.exclude(action=Entity.INITIAL).first()).data
                if lot_data:
                    chain.append(lot_data)
        elif package.type == Package.LOT:
            sacs = Entity.objects.filter(package__type=Package.SAC, package__lot=package)
            for sac_entity in sacs:
                for harvest_entity in Entity.objects.filter(
                        package__type=Package.HARVEST, package__sac=sac_entity.package
                ):
                    chain.append(ChainSeriazlier(harvest_entity).data)
                chain.append(ChainSeriazlier(sac_entity).data)
            for entity in package.package_entities.exclude(action=Entity.INITIAL):
                chain.append(ChainSeriazlier(entity).data)
        return Response(chain, status=status.HTTP_200_OK)
