import json
import pytz
import base64
import requests
import os

from datetime import datetime

from django.shortcuts import get_object_or_404, get_list_or_404
from django.db import transaction
from django.db.models import Q
from django.contrib.gis.geos import Point
from django.conf import settings

from rest_framework import serializers
from rest_framework.exceptions import NotFound

from apps.blockchain.transaction import PayloadFactory
from apps.entities.models import (
    Entity, Package, LoggingBeginning, LoggingEnding, CarbonizationBeginning, CarbonizationEnding, Oven,
    Bag, LoadingTransport, Reception, ReceptionImage, Replantation
)
from apps.additional_data.exceptions import InvalidAgentRoleError
from apps.api.v1.entities.exceptions import EntityAlreadyExistException
from protos.entity_pb2 import Package as PackageProto

from google.protobuf.message import DecodeError
from protos.payload_pb2 import SCPayload


class OvenSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Oven
        fields = ('id', 'oven_id')


class EntitySerializer(serializers.ModelSerializer):
    properties = serializers.JSONField()
    pid = serializers.CharField(max_length=100, required=False)
    documents_photos = serializers.ListField(child=serializers.ImageField(), required=False)
    receipt_photos = serializers.ListField(child=serializers.ImageField(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location'].required = True

    class Meta:
        model = Entity
        fields = ('action', 'timestamp', 'properties', 'pid', 'location', 'documents_photos', 'receipt_photos')

    def validate_location(self, data):
        if type(data) != dict:
            data = json.loads(data)
        data = Point(data['longitude'], data['latitude'])
        return data

    @transaction.atomic
    def create(self, validated_data):
        properties_data = validated_data.pop('properties')
        pid = validated_data.pop('pid') if 'pid' in validated_data else None
        action = validated_data['action']
        if pid and action in [Entity.LOGGING_BEGINNING, Entity.LOGGING_ENDING]:
            package, created = Package.objects.get_or_create(pid=pid)
            if action == Entity.LOGGING_ENDING:
                get_object_or_404(Entity, package=package, action=Entity.LOGGING_BEGINNING)
        elif pid and action in [Entity.CARBONIZATION_BEGINNING, Entity.CARBONIZATION_ENDING]:
            package_kwargs = {'pid': pid, 'type': Package.HARVEST}
            if action == Entity.CARBONIZATION_BEGINNING:
                package_kwargs['plot_id'] = properties_data.pop('plot_id')
            package, created = Package.objects.get_or_create(**package_kwargs)
            if action == Entity.CARBONIZATION_ENDING:
                get_list_or_404(Entity, package=package, action=Entity.CARBONIZATION_BEGINNING)
        elif pid and action == Entity.LOADING_TRANSPORT:
            harvest_id = properties_data.pop('harvest_id')
            package, created = Package.objects.get_or_create(pid=pid, type=Package.TRUCK, harvest_id=harvest_id)
        elif action == Entity.RECEPTION:
            qr_code = properties_data['bags_qr_codes'][0]
            # qr codes are reusable after reception in any other chain
            package = Package.objects.filter(
                package_entities__loadingtransport__bags__qr_code=qr_code,
                type=Package.TRUCK,
                last_action__action=Entity.LOADING_TRANSPORT
            ).order_by('id').last()
            if not package:
                raise NotFound(detail=f'Truck with this bag ({qr_code}) not found.')
            properties_data['documents_photos'] = validated_data.pop('documents_photos', [])
            properties_data['receipt_photos'] = validated_data.pop('receipt_photos', [])
        else:
            raise NotFound(detail='Please check your data in request body.')
        if action not in [Entity.CARBONIZATION_BEGINNING, Entity.CARBONIZATION_ENDING] \
                and Entity.objects.filter(package=package, action=action).exists():
            raise EntityAlreadyExistException()
        entity = Entity.objects.create(
            user=self.context['request'].user,
            package=package,
            **validated_data
        )
        try:
            create_action = getattr(self, "_create_{}".format(entity.get_action_display().lower().replace(' &', '').replace(' ', '_')))
        except AttributeError:
            raise NotFound(detail=f'Action type "{action}" not found.')
        create_action(entity, properties_data)
        package.last_action = entity
        package.save()
        return entity

    @staticmethod
    def _create_logging_beginning(entity, properties_data):
        if not (entity.user.is_logger or entity.user.is_carbonizer or entity.user.is_superuser_role):
            raise InvalidAgentRoleError("Only Logger or Carbonizer can add logging beginning.")
        parcel_id = properties_data.pop('parcel')
        village_id = properties_data.pop('village')
        tree_specie_id = properties_data.pop('tree_specie')
        properties_data['beginning_date'] = properties_data.get('beginning_date') or properties_data.pop('event_date')
        logging_beginning, created = LoggingBeginning.objects.get_or_create(
            entity=entity,
            parcel_id=parcel_id,
            village_id=village_id,
            tree_specie_id=tree_specie_id,
            **properties_data
        )
        if created:
            entity.package.add_to_chain(entity.user, PackageProto.PLOT, PayloadFactory.Types.CREATE_PACKAGE)

    @staticmethod
    def _create_logging_ending(entity, properties_data):
        if not (entity.user.is_logger or entity.user.is_carbonizer or entity.user.is_superuser_role):
            raise InvalidAgentRoleError("Only Logger or Carbonizer can add logging ending.")
        properties_data['ending_date'] = properties_data.get('ending_date') or properties_data.pop('event_date')
        logging_ending, created = LoggingEnding.objects.get_or_create(
            entity=entity,
            **properties_data
        )
        if created:
            entity.update_in_chain()

    @staticmethod
    def _create_carbonization_beginning(entity, properties_data):
        if not (entity.user.is_carbonizer or entity.user.is_superuser_role):
            raise InvalidAgentRoleError("Only Carbonizer can add carbonization beginning.")
        oven_id = properties_data.pop('oven_id')
        if CarbonizationBeginning.objects.filter(oven__oven_id=oven_id, entity__package=entity.package).exists():
            raise serializers.ValidationError('Oven ID already exists!')
        oven_type_id = properties_data.pop('oven_type')
        oven = Oven.objects.create(oven_id=oven_id)
        properties_data['beginning_date'] = properties_data.get('beginning_date') or properties_data.pop('event_date')
        carbonization_beginning, created = CarbonizationBeginning.objects.get_or_create(
            entity=entity,
            oven=oven,
            oven_type_id=oven_type_id,
            **properties_data
        )
        if created:
            carbonization_beginning.add_to_chain(entity.user, PackageProto.HARVEST, PayloadFactory.Types.CREATE_PACKAGE)

    @staticmethod
    def _create_carbonization_ending(entity, properties_data):
        if not (entity.user.is_carbonizer or entity.user.is_superuser_role):
            raise InvalidAgentRoleError("Only Carbonizer can add carbonization ending.")
        oven_id = properties_data.pop('oven_id')
        try:
            oven = Oven.objects.get(oven_id=oven_id, carbonization_beginning__entity__package=entity.package)
            properties_data['end_date'] = properties_data.get('end_date') or properties_data.pop('event_date')
            carbonization_ending, created = CarbonizationEnding.objects.get_or_create(
                entity=entity,
                oven=oven,
                **properties_data
            )
            if created:
                entity.update_in_chain()
        except Oven.DoesNotExist:
            raise NotFound(detail='Oven not found.')

    @staticmethod
    def _create_loading_transport(entity, properties_data):
        if not (entity.user.is_carbonizer or entity.user.is_superuser_role):
            raise InvalidAgentRoleError("Only Carbonizer can add loading transport.")
        bags_qr_codes = properties_data.pop('bags_qr_codes')
        destination_id = properties_data.pop('destination')
        properties_data['loading_date'] = properties_data.get('loading_date') or properties_data.pop('event_date')
        loading_transport, created = LoadingTransport.objects.get_or_create(
            entity=entity,
            destination_id=destination_id,
            **properties_data
        )
        harvest_pid = entity.package.harvest.pid
        if created:
            bags = (Bag(pid=f'{harvest_pid}/B{i+1:03d}', qr_code=qr_code, transport_id=loading_transport.id)
                    for i, qr_code in enumerate(bags_qr_codes))
            Bag.objects.bulk_create(bags)
            entity.package.add_to_chain(entity.user, PackageProto.TRUCK, PayloadFactory.Types.CREATE_PACKAGE)

    @staticmethod
    def _create_reception(entity, properties_data):
        if not (entity.user.is_director or entity.user.is_superuser_role):
            raise InvalidAgentRoleError("Only Director can add reception.")
        bags_qr_codes = properties_data.pop('bags_qr_codes')
        documents_photos = properties_data.pop('documents_photos')
        receipt_photos = properties_data.pop('receipt_photos')
        properties_data['reception_date'] = properties_data.get('reception_date') or properties_data.pop('event_date')
        reception, created = Reception.objects.get_or_create(
            entity=entity,
            **properties_data
        )
        if created:
            Bag.objects.filter(qr_code__in=bags_qr_codes, transport__entity__package=entity.package).update(reception=reception)
            photos = [ReceptionImage(image=image, type=ReceptionImage.DOCUMENT, reception_id=reception.id)
                    for image in documents_photos]
            photos.extend([ReceptionImage(image=image, type=ReceptionImage.RECEIPT, reception_id=reception.id)
                    for image in receipt_photos])
            ReceptionImage.objects.bulk_create(photos)
            entity.update_in_chain()


class PackagePidSerializer(serializers.ModelSerializer):
    action = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = ('pid', 'id', 'action')

    def get_action(self, obj):
        return obj.last_action.action if obj.last_action else ""


class EntityListSerializer(serializers.ModelSerializer):
    pid = serializers.SerializerMethodField()

    class Meta:
        model = Entity
        fields = ('pid', 'action',)

    def get_pid(self, obj):
        return obj.package.pid


class SimpleEntitySerializer(serializers.ModelSerializer):
    timestamp_display = serializers.SerializerMethodField()
    description = serializers.CharField(source='web_description')
    timezone = serializers.SerializerMethodField()
    location_display = serializers.SerializerMethodField()
    event_date = serializers.SerializerMethodField()
    user_code = serializers.CharField(source='user.code')

    class Meta:
        model = Entity
        fields = ('description', 'timestamp_display', 'timezone', 'location_display', 'timestamp', 'id', 'action',
                  'event_date', 'user_code')

    def get_event_date(self, obj):
        action = getattr(obj, Entity.CHILD_MODEL_NAMES[obj.action])
        for key in ('beginning_date', 'ending_date', 'end_date', 'loading_date', 'reception_date'):
            if hasattr(action, key):
                return getattr(action, key)
        return 0

    def get_timezone(self, obj):
        return datetime.fromtimestamp(obj.timestamp, tz=pytz.timezone(settings.TIME_ZONE)).strftime('%Z%z')

    def get_timestamp_display(self, obj):
        return datetime.fromtimestamp(obj.timestamp, tz=pytz.timezone(settings.TIME_ZONE)).strftime('%d/%m/%Y %H:%M')

    def get_location_display(self, obj):
        return [obj.location.y, obj.location.x]


class PackagesSerializer(serializers.ModelSerializer):
    type_display = serializers.SerializerMethodField()
    entities = SimpleEntitySerializer(many=True, source='package_entities')
    plot_has_replantation = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = ('id', 'pid', 'type', 'type_display', 'entities', 'plot_has_replantation', 'is_finished')

    def get_type_display(self, obj):
        return obj.get_type_display().lower()

    def get_plot_has_replantation(self, obj):
        try:
            return obj.type == Package.PLOT and obj.replantation is not None
        except AttributeError:
            pass
        return False


class EntityDetailsSerializer(SimpleEntitySerializer):
    location_display = serializers.SerializerMethodField()
    action_display = serializers.CharField(source='get_action_display')
    blockchain_details = serializers.SerializerMethodField()
    user_code = serializers.CharField(source='user.code')

    class Meta:
        model = Entity
        fields = ('description', 'timestamp_display', 'timezone', 'action_display', 'user_id', 'location_display',
                  'blockchain_details', 'user_code', 'timestamp', 'id')

    def get_blockchain_details(self, obj):
        if obj.blockchain_batch_id:
            request = self.context['request']
            http = 'https' if request.is_secure() else 'http'
            r = requests.get(
                f"{http}://{os.environ.get('API_HOST')}:{os.environ.get('API_PORT')}/batches/{obj.blockchain_batch_id}")
            try:
                transaction = r.json()['data']['transactions'][0]
                payload = base64.b64decode(transaction['payload'])
                try:
                    t = SCPayload()
                    t.ParseFromString(payload)
                    payload = str(t).replace('\n', '</br>')
                    if t.timestamp:
                        readable_timestamp = self.get_timestamp_display(t)
                        payload = payload.replace(str(t.timestamp), readable_timestamp)
                    transaction['payload'] = payload
                except DecodeError:
                    transaction['payload'] = 'System transaction'
            except (KeyError, IndexError):
                transaction = {}

            return transaction
        return {}

    def deg_to_dms(self, deg, x=True):
        d = int(deg)
        md = abs(deg - d) * 60
        m = int(md)
        sd = (md - m) * 60
        if d < 0:
            direction = 'W' if x else 'S'
        else:
            direction = 'E' if x else 'N'

        return f'{abs(d)}°{m}\'{sd:.1f}"{direction}'

    def get_location_display(self, obj):
        return f'{self.deg_to_dms(obj.location.y, x=False)} {self.deg_to_dms(obj.location.x)}'


class BaseEntityActionSerializer(serializers.Serializer):
    entity = EntityDetailsSerializer()

    def parse_timestamp_to_str_date(self, timestamp):
        return datetime.fromtimestamp(timestamp, tz=pytz.timezone(settings.TIME_ZONE)).strftime('%d/%m/%Y')


class LoggingBeginningSerializer(BaseEntityActionSerializer, serializers.ModelSerializer):
    beginning_date_display = serializers.SerializerMethodField()
    village = serializers.CharField(source='village.name')
    tree_specie = serializers.CharField(source='tree_specie.name')

    class Meta:
        model = LoggingBeginning
        fields = ('entity', 'beginning_date_display', 'village', 'tree_specie', 'beginning_date', 'parcel_id')

    def get_beginning_date_display(self, obj):
        return self.parse_timestamp_to_str_date(obj.beginning_date)


class LoggingEndingSerializer(BaseEntityActionSerializer, serializers.ModelSerializer):
    ending_date_display = serializers.SerializerMethodField()

    class Meta:
        model = LoggingEnding
        fields = ('entity', 'ending_date_display', 'number_of_trees', 'ending_date')

    def get_ending_date_display(self, obj):
        return self.parse_timestamp_to_str_date(obj.ending_date)


class BagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bag
        fields = ('pid', 'qr_code', 'id')


class LoadingTransportSerializer(BaseEntityActionSerializer, serializers.ModelSerializer):
    loading_date_display = serializers.SerializerMethodField()
    bags = BagSerializer(many=True)
    scanned_bags = serializers.SerializerMethodField()

    class Meta:
        model = LoadingTransport
        fields = ('entity', 'plate_number', 'loading_date_display', 'bags', 'scanned_bags', 'loading_date', 'destination_id')

    def get_scanned_bags(self, obj):
        return obj.bags.count()

    def get_loading_date_display(self, obj):
        return self.parse_timestamp_to_str_date(obj.loading_date)


class ReceptionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceptionImage
        fields = ('image',)


class ReceptionSerializer(BaseEntityActionSerializer, serializers.ModelSerializer):
    bags = BagSerializer(many=True)
    scanned_bags = serializers.SerializerMethodField()
    documents_photos = serializers.SerializerMethodField()
    receipt_photos = serializers.SerializerMethodField()
    reception_date_display = serializers.SerializerMethodField()

    class Meta:
        model = Reception
        fields = ('entity', 'bags', 'scanned_bags', 'documents_photos', 'receipt_photos', 'reception_date_display', 'reception_date')

    def get_reception_date_display(self, obj):
        if obj.reception_date:
            return self.parse_timestamp_to_str_date(obj.reception_date)
        return ''

    def get_scanned_bags(self, obj):
        return obj.bags.count()

    def get_documents_photos(self, obj):
        return ReceptionImageSerializer(obj.images.filter(type=ReceptionImage.DOCUMENT), many=True).data

    def get_receipt_photos(self, obj):
        return ReceptionImageSerializer(obj.images.filter(type=ReceptionImage.RECEIPT), many=True).data


class CarbonizationBeginningSerializer(BaseEntityActionSerializer, serializers.ModelSerializer):
    beginning_date_display = serializers.SerializerMethodField()
    oven_type_display = serializers.CharField(source='oven_type.name')
    timber_volume = serializers.SerializerMethodField()

    class Meta:
        model = CarbonizationBeginning
        fields = ('entity', 'beginning_date_display', 'oven_type_display', 'oven_measurements', 'timber_volume', 'beginning_date')

    def get_timber_volume(self, obj):
        result = 1
        measurements = obj.oven_measurements
        try:
            for key in measurements:
                result *= measurements[key]
            return result
        except TypeError:
            return 0

    def get_beginning_date_display(self, obj):
        return self.parse_timestamp_to_str_date(obj.beginning_date)


class CarbonizationEndingSerializer(BaseEntityActionSerializer, serializers.ModelSerializer):

    class Meta:
        model = CarbonizationEnding
        fields = '__all__'


class PackageOvenSerializer(serializers.ModelSerializer):
    carbonization_beginning = serializers.SerializerMethodField()
    carbonization_ending = serializers.SerializerMethodField()

    class Meta:
        model = Oven
        fields = ('id', 'oven_id', 'carbonization_beginning', 'carbonization_ending')

    def get_carbonization_beginning(self, obj):
        if obj.carbonization_beginning:
            return CarbonizationBeginningSerializer(
                obj.carbonization_beginning,
                context=self.context).data
        return {}

    def get_carbonization_ending(self, obj):
        if hasattr(obj, 'carbonization_ending'):
            return CarbonizationEndingSerializer(
                obj.carbonization_ending,
                context=self.context).data
        return {}


class PlotPackageSerializer(serializers.ModelSerializer):
    logging_beginning = serializers.SerializerMethodField()
    logging_ending = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = (
            'logging_beginning', 'logging_ending'
        )

    def get_logging_beginning(self, obj):
        try:
            return LoggingBeginningSerializer(
                obj.package_entities.get(action=Entity.LOGGING_BEGINNING).loggingbeginning,
                context=self.context).data
        except Entity.DoesNotExist:
            return {}

    def get_logging_ending(self, obj):
        try:
            return LoggingEndingSerializer(
                obj.package_entities.get(action=Entity.LOGGING_ENDING).loggingending,
                context=self.context).data
        except Entity.DoesNotExist:
            return {}


class HarvestPackageSerializer(serializers.ModelSerializer):
    ovens = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = ('ovens',)

    def get_ovens(self, obj):
        return PackageOvenSerializer(Oven.objects.filter(
            Q(carbonization_beginning__entity__package_id=obj.id) |
            Q(carbonization_ending__entity__package_id=obj.id)
        ).order_by('oven_id'), many=True, context=self.context).data


class TruckPackageSerializer(serializers.ModelSerializer):
    loading_transport = serializers.SerializerMethodField()
    reception = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = (
            'loading_transport', 'reception'
        )

    def get_loading_transport(self, obj):
        try:
            return LoadingTransportSerializer(
                obj.package_entities.get(action=Entity.LOADING_TRANSPORT).loadingtransport,
                context=self.context).data
        except Entity.DoesNotExist:
            return {}

    def get_reception(self, obj):
        try:
            return ReceptionSerializer(
                obj.package_entities.get(action=Entity.RECEPTION).reception,
                context=self.context).data
        except Entity.DoesNotExist:
            return {}


class PackageDetailsSerializer(serializers.ModelSerializer):
    type_display = serializers.SerializerMethodField()
    properties = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = ('id', 'pid', 'type_display', 'properties', 'is_finished')

    def get_type_display(self, obj):
        return obj.get_type_display().lower()

    def get_properties(self, obj):
        try:
            properties = getattr(self,
                                 "_{}_properties".format(obj.get_type_display().lower().replace(' ', '_')))
        except AttributeError:
            return ""
        return properties(obj)

    def _plot_properties(self, obj):
        return PlotPackageSerializer(obj, context=self.context).data

    def _harvest_properties(self, obj):
        return HarvestPackageSerializer(obj, context=self.context).data

    def _transport_properties(self, obj):
        return TruckPackageSerializer(obj, context=self.context).data


class ReplantationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Replantation
        exclude = ('blockchain_batch_id', 'user')

    def validate_location(self, data):
        if type(data) != dict:
            data = json.loads(data)
        data = Point(data['longitude'], data['latitude'])
        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        obj = super().create(validated_data)
        obj.add_to_chain(PayloadFactory.Types.CREATE_REPLANTATION)
        return obj


class ReplantationListSerializer(serializers.ModelSerializer):
    trees_cut = serializers.SerializerMethodField()
    trees_planted_dates_display = serializers.SerializerMethodField()
    trees_cut_dates_display = serializers.SerializerMethodField()
    ending_date_display = serializers.SerializerMethodField()
    pid = serializers.CharField(source='plot.pid')
    entities = serializers.SerializerMethodField()
    type_display = serializers.SerializerMethodField()
    blockchain_details = serializers.SerializerMethodField()
    trees_planted_dates = serializers.SerializerMethodField()
    trees_cut_dates = serializers.SerializerMethodField()

    class Meta:
        model = Replantation
        fields = ('pid', 'trees_planted', 'trees_cut', 'ending_date_display', 'trees_cut_dates_display',
                  'trees_planted_dates_display', 'entities', 'type_display', 'blockchain_details',
                  'ending_date', 'trees_planted_dates', 'trees_cut_dates')

    def get_blockchain_details(self, obj):
        if obj.blockchain_batch_id:
            request = self.context['request']
            http = 'https' if request.is_secure() else 'http'
            r = requests.get(
                f"{http}://{os.environ.get('API_HOST')}:{os.environ.get('API_PORT')}/batches/{obj.blockchain_batch_id}")
            try:
                transaction = r.json()['data']['transactions'][0]
                payload = base64.b64decode(transaction['payload'])
                try:
                    t = SCPayload()
                    t.ParseFromString(payload)
                    payload = str(t).replace('\n', '</br>')
                    if t.timestamp:
                        readable_timestamp = self.parse_timestamp_to_str_datetime(t.timestamp)
                        payload = payload.replace(str(t.timestamp), readable_timestamp)
                    transaction['payload'] = payload
                except DecodeError:
                    transaction['payload'] = 'System transaction'
            except (KeyError, IndexError):
                transaction = {}

            return transaction
        return {}


    def get_type_display(self, obj):
        return 'replantation'

    def get_entities(self, obj):
        # add data for map component
        return [{
            'description': f'Planted {obj.trees_planted} tree{"s" if obj.trees_planted > 1 else ""}',
            'location_display': [obj.location.y, obj.location.x]
        }]

    def parse_timestamp_to_str_date(self, timestamp):
        return datetime.fromtimestamp(timestamp, tz=pytz.timezone(settings.TIME_ZONE)).strftime('%d/%m/%Y')

    def parse_timestamp_to_str_datetime(self, timestamp):
        return datetime.fromtimestamp(timestamp, tz=pytz.timezone(settings.TIME_ZONE)).strftime('%d/%m/%Y %H:%M')

    def get_ending_date_display(self, obj):
        return self.parse_timestamp_to_str_datetime(obj.ending_date)

    def get_trees_cut(self, obj):
        try:
            return obj.plot.package_entities.get(action=Entity.LOGGING_ENDING).loggingending.number_of_trees
        except:
            return 0

    def get_trees_cut_dates_display(self, obj):
        try:
            logging_beginning = obj.plot.package_entities.get(action=Entity.LOGGING_BEGINNING).loggingbeginning.beginning_date
        except:
            logging_beginning = 0
        try:
            logging_ending = obj.plot.package_entities.get(action=Entity.LOGGING_ENDING).loggingending.ending_date
        except:
            logging_ending = 0
        return f'{self.parse_timestamp_to_str_date(logging_beginning)} - {self.parse_timestamp_to_str_date(logging_ending)}'

    def get_trees_cut_dates(self, obj):
        try:
            logging_beginning = obj.plot.package_entities.get(action=Entity.LOGGING_BEGINNING).loggingbeginning.beginning_date
        except:
            logging_beginning = 0
        try:
            logging_ending = obj.plot.package_entities.get(action=Entity.LOGGING_ENDING).loggingending.ending_date
        except:
            logging_ending = 0
        return [logging_beginning, logging_ending]

    def get_trees_planted_dates_display(self, obj):
        return f'{self.parse_timestamp_to_str_date(obj.beginning_date)} - {self.parse_timestamp_to_str_date(obj.ending_date)}'

    def get_trees_planted_dates(self, obj):
        return [obj.beginning_date, obj.ending_date]

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['trees_planted_percent'] = instance.trees_planted / (instance.trees_planted + repr['trees_cut']) * 100
        return repr
