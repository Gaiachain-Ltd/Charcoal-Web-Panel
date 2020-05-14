import json

from django.shortcuts import get_object_or_404, get_list_or_404
from django.db import transaction
from django.contrib.gis.geos import Point
from django.templatetags.static import static

from rest_framework import serializers
from rest_framework.exceptions import NotFound

from apps.entities.models import (
    Entity, Package, LoggingBeginning, LoggingEnding, CarbonizationBeginning, CarbonizationEnding, Oven,
    Bag, LoadingTransport, Checkpoint, Reception
)
from apps.additional_data.models import (
    Parcel, Village
)
from apps.users.serializers import (
    UserSerializer,
)
from apps.entities.exceptions import PackageAlreadyExistException, EntityAlreadyExistException
from apps.entities.utils import unix_to_datetime_tz


class VillageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Village
        fields = ('name', 'id')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id'].read_only = False


class ParcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = ('name', 'id', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id'].read_only = False

class OvenSerializer(serializers.ModelSerializer):

    class Meta:
        model = Oven
        fields = ('id', 'oven_id')
# class HarvestSerializer(serializers.ModelSerializer):
#     village = VillageSerializer(required=False)
#     short_description = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Harvest
#         fields = ('parcel', 'producer', 'village', 'harvest_date', 'short_description',)
#
#     def get_short_description(self, obj):
#         return obj.short_description
#
#
# class BreakingSerializer(serializers.ModelSerializer):
#     short_description = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Breaking
#         fields = ('breaking_date', 'end_fermentation_date', 'beans_volume', 'short_description',)
#
#     def get_short_description(self, obj):
#         return obj.short_description
#
#
# class ReceptionSerializer(serializers.ModelSerializer):
#     short_description = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Reception
#         fields = ('reception_date', 'transport_date', 'buyer', 'short_description',)
#
#     def get_short_description(self, obj):
#         return obj.short_description
#
#
# class BaggingSerializer(serializers.ModelSerializer):
#     harvest_weights = serializers.SerializerMethodField(read_only=True)
#     short_description = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Bagging
#         fields = ('harvest_weights', 'short_description',)
#
#     def get_harvest_weights(self, obj):
#         return Package.objects.filter(type=Package.HARVEST, sac=obj.entity.package).values('pid', 'weight')
#
#     def get_short_description(self, obj):
#         return obj.short_description
#
#
# class LotCreationSerializer(serializers.ModelSerializer):
#     short_description = serializers.SerializerMethodField()
#
#     class Meta:
#         model = LotCreation
#         fields = ('notes', 'short_description',)
#
#     def get_short_description(self, obj):
#         return obj.short_description
#
#
# class TransportSerializer(serializers.ModelSerializer):
#     short_description = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Transport
#         fields = ('transporter', 'transport_date', 'destination', 'short_description',)
#
#     def get_short_description(self, obj):
#         return obj.short_description
#
#
# class LotReceptionSerializer(serializers.ModelSerializer):
#     short_description = serializers.SerializerMethodField()
#
#     class Meta:
#         model = LotReception
#         fields = ('weight', 'short_description',)
#
#     def get_short_description(self, obj):
#         return obj.short_description


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ('pid',)


class EntitySerializer(serializers.ModelSerializer):
    properties = serializers.JSONField()
    pid = serializers.CharField(max_length=50, required=False)
    qr_code = serializers.CharField(max_length=14, required=False)
    photo = serializers.ImageField(required=False)
    documents_photo = serializers.ImageField(required=False)
    receipt_photo = serializers.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location'].required = True

    class Meta:
        model = Entity
        fields = ('action', 'timestamp', 'properties', 'pid', 'qr_code', 'location', 'photo', 'documents_photo', 'receipt_photo')

    def validate_location(self, data):
        if type(data) != dict:
            data = json.loads(data)
        data = Point(data['longitude'], data['latitude'])
        return data

    @transaction.atomic
    def create(self, validated_data):
        properties_data = validated_data.pop('properties')
        qr_code = validated_data.pop('qr_code') if 'qr_code' in validated_data else None
        pid = validated_data.pop('pid') if 'pid' in validated_data else None
        action = validated_data['action']
        if pid and action in [Entity.LOGGING_BEGINNING, Entity.LOGGING_ENDING]:
            package, created = Package.objects.get_or_create(pid=pid)
            if action == Entity.LOGGING_ENDING:
                get_object_or_404(Entity, package=package, action=Entity.LOGGING_BEGINNING)
        elif pid and action in [Entity.CARBONIZATION_BEGINNING, Entity.CARBONIZATION_ENDING]:
            package, created = Package.objects.get_or_create(pid=pid, type=Package.HARVEST)
            if action == Entity.CARBONIZATION_ENDING:
                get_list_or_404(Entity, package=package, action=Entity.CARBONIZATION_BEGINNING)
        elif pid and action == Entity.LOADING_TRANSPORT:
            package, created = Package.objects.get_or_create(pid=pid, type=Package.TRUCK)
        elif qr_code and action in [Entity.CHECKPOINT_SODEFOR, Entity.CHECKPOINT_FOREST]:
            try:
                package = Package.objects.get(package_entities__loadingtransport__bags__qr_code=qr_code)
                properties_data['qr_code'] = qr_code
                properties_data['photo'] = validated_data.pop('photo')
            except Package.DoesNotExist:
                raise NotFound(detail=f'Truck with this bag ({qr_code}) not found.')
        elif action == Entity.RECEPTION:
            try:
                package = Package.objects.get(
                    package_entities__loadingtransport__bags__qr_code=properties_data['bags_qr_codes'][0]
                )
                properties_data['documents_photo'] = validated_data.pop('documents_photo')
                properties_data['receipt_photo'] = validated_data.pop('receipt_photo')
            except Package.DoesNotExist:
                raise NotFound(detail=f'Truck with this bag ({qr_code}) not found.')
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
        # if not entity.user.is_inspector:
        #     raise InvalidAgentRoleError("Only Inspector can create harvest.")
        parcel_id = properties_data.pop('parcel')
        village_id = properties_data.pop('village')
        tree_specie_id = properties_data.pop('tree_specie')
        logging_beginning, created = LoggingBeginning.objects.get_or_create(
            entity=entity,
            parcel_id=parcel_id,
            village_id=village_id,
            tree_specie_id=tree_specie_id,
            **properties_data
        )
        # if created:
        #     logging_beginning.add_to_chain()

    @staticmethod
    def _create_logging_ending(entity, properties_data):
        # if not entity.user.is_inspector:
        #     raise InvalidAgentRoleError("Only Inspector can create harvest.")
        logging_ending, created = LoggingEnding.objects.get_or_create(
            entity=entity,
            **properties_data
        )
        # if created:
        #     logging_ending.update_in_chain()

    @staticmethod
    def _create_carbonization_beginning(entity, properties_data):
        # if not entity.user.is_inspector:
        #     raise InvalidAgentRoleError("Only Inspector can create harvest.")
        oven_id = properties_data.pop('oven_id')
        plot_id = properties_data.pop('plot_id')
        oven_type_id = properties_data.pop('oven_type')
        oven = Oven.objects.create(oven_id=oven_id)
        carbonization_beginning, created = CarbonizationBeginning.objects.get_or_create(
            entity=entity,
            oven=oven,
            plot_id=plot_id,
            oven_type_id=oven_type_id,
            **properties_data
        )
        # if created:
        #     carbonization_beginning.add_to_chain()

    @staticmethod
    def _create_carbonization_ending(entity, properties_data):
        # if not entity.user.is_inspector:
        #     raise InvalidAgentRoleError("Only Inspector can create harvest.")
        oven_ids = properties_data.pop('oven_ids')
        harvest_id = properties_data.pop('harvest')
        ovens = Oven.objects.filter(id__in=oven_ids)
        carbonization_ending, created = CarbonizationEnding.objects.get_or_create(
            entity=entity,
            harvest_id=harvest_id,
            **properties_data
        )
        if created:
            carbonization_ending.ovens.add(*ovens)
            # carbonization_ending.update_in_chain()

    @staticmethod
    def _create_loading_transport(entity, properties_data):
        # if not entity.user.is_inspector:
        #     raise InvalidAgentRoleError("Only Inspector can create harvest.")
        bags_qr_codes = properties_data.pop('bags_qr_codes')
        harvest_id = properties_data.pop('harvest')
        destination_id = properties_data.pop('destination')
        loading_transport, created = LoadingTransport.objects.get_or_create(
            entity=entity,
            harvest_id=harvest_id,
            destination_id=destination_id,
            **properties_data
        )
        harvest_pid = loading_transport.harvest.pid
        if created:
            bags = (Bag(pid=f'{harvest_pid}/B{i+1:03d}', qr_code=qr_code, transport_id=loading_transport.id)
                    for i, qr_code in enumerate(bags_qr_codes))
            Bag.objects.bulk_create(bags)
            # loading_transport.add_to_chain()

    @staticmethod
    def _create_checkpoint(entity, properties_data):
        # if not entity.user.is_inspector:
        #     raise InvalidAgentRoleError("Only Inspector can create harvest.")
        checkpoint, created = Checkpoint.objects.get_or_create(
            entity=entity,
            **properties_data
        )
        # if created:
        #     checkpoint.update_in_chain()

    def _create_checkpoint_eaux_et_forest(self, entity, properties_data):
        self._create_checkpoint(entity, properties_data)

    def _create_checkpoint_sodefor(self, entity, properties_data):
        self._create_checkpoint(entity, properties_data)

    @staticmethod
    def _create_reception(entity, properties_data):
        # if not entity.user.is_inspector:
        #     raise InvalidAgentRoleError("Only Inspector can create harvest.")
        bags_qr_codes = properties_data.pop('bags_qr_codes')
        reception, created = Reception.objects.get_or_create(
            entity=entity,
            **properties_data
        )
        if created:
            Bag.objects.filter(qr_code__in=bags_qr_codes).update(reception=reception)
        #     reception.update_in_chain()


class PackagePidSerializer(serializers.ModelSerializer):
    action = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = ('pid', 'action')

    def get_action(self, obj):
        return obj.last_action.action if obj.last_action else ""


class EntityBatchSerializer(serializers.Serializer):
    pids = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=True
    )


class EntityListSerializer(serializers.ModelSerializer):
    pid = serializers.SerializerMethodField()

    class Meta:
        model = Entity
        fields = ('pid', 'action',)

    def get_pid(self, obj):
        return obj.package.pid


class EntityBatchListSerializer(serializers.ModelSerializer):
    pid = serializers.SerializerMethodField()
    user = UserSerializer()
    properties = serializers.SerializerMethodField()
    qr_code = serializers.SerializerMethodField()
    relations = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    class Meta:
        model = Entity
        fields = ('pid', 'action', 'timestamp', 'user', 'qr_code', 'relations', 'properties', 'location')

    def get_weight(self, obj):
        if not obj.package:
            return 0
        return obj.package.weight or 0

    def get_location(self, obj):
        if not obj.location:
            return {
                'latitude': "",
                'longitude': ""
            }
        return {
            'latitude': obj.location.x,
            'longitude': obj.location.y
        }

    def get_relations(self, obj):
        related_pids = []
        if obj.package.type == Package.HARVEST:
            related_pids = [{'pid': obj.package.sac.pid, 'type': obj.package.sac.type}] if obj.package.sac else []
        elif obj.package.type == Package.SAC:
            related_pids = list(obj.package.package_harvests.values('pid', 'type'))
            if obj.package.lot:
                lot = {'pid': obj.package.lot.pid, 'type': obj.package.lot.type}
                related_pids.append(lot)
        elif obj.package.type == Package.LOT:
            related_pids = list(obj.package.package_sacs.values('pid', 'type'))
        return related_pids

    def get_pid(self, obj):
        return obj.package.pid

    def get_qr_code(self, obj):
        return obj.package.qr_code

    def get_properties(self, obj):
        try:
            properties = getattr(self, "_{}_properties".format(obj.get_action_display().lower().replace(' ', '_')))
        except AttributeError:
            return ""
            # raise NotFound(detail='Action type "{}" not found.'.format(obj.get_action_display()))
        return properties(obj)

    @staticmethod
    def _harvest_properties(obj):
        return HarvestSerializer(obj.harvest).data

    @staticmethod
    def _breaking_properties(obj):
        return BreakingSerializer(obj.breaking).data

    @staticmethod
    def _harvest_reception_properties(obj):
        return ReceptionSerializer(obj.reception).data

    @staticmethod
    def _bagging_properties(obj):
        return BaggingSerializer(obj.bagging).data

    @staticmethod
    def _lot_creation_properties(obj):
        return LotCreationSerializer(obj.lotcreation).data

    @staticmethod
    def _transport_properties(obj):
        return TransportSerializer(obj.transport).data

    @staticmethod
    def _lot_reception_properties(obj):
        return LotReceptionSerializer(obj.lotreception).data


class HarvestsSerializer(serializers.Serializer):
    HARVEST = 'HA'
    BREAKING = 'BR'
    ACTIONS = [
        (HARVEST, 'Harvest'),
        (BREAKING, 'Breaking'),
    ]
    last_action = serializers.ChoiceField(choices=ACTIONS, required=False)


class PackagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ('id', 'pid', 'type')


class HarvestPackageSerializer(serializers.ModelSerializer):
    producer_name = serializers.SerializerMethodField()
    producer_pid = serializers.SerializerMethodField()
    village = serializers.SerializerMethodField()
    harvest_date = serializers.SerializerMethodField()
    breaking_date = serializers.SerializerMethodField()
    weight = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = (
            'producer_name', 'producer_pid', 'village', 'harvest_date', 'breaking_date', 'weight',
        )

    def get_weight(self, obj):
        weight = "{} kg".format(obj.weight) if obj.weight else ""
        return {"Estimated volume on fresh beans kg": weight}

    def get_producer_name(self, obj):
        try:
            return {"Producer name": obj.package_entities.get(action=Entity.HARVEST).harvest.producer.name}
        except Entity.DoesNotExist:
            return {"Producer name": ""}

    def get_producer_pid(self, obj):
        try:
            return {"Producer ID": obj.package_entities.get(action=Entity.HARVEST).harvest.producer.pid}
        except Entity.DoesNotExist:
            return {"Producer ID": ""}

    def get_village(self, obj):
        try:
            return {'Village': obj.package_entities.get(action=Entity.HARVEST).harvest.producer.village.name}
        except Entity.DoesNotExist:
            return {'Village': ""}

    def get_harvest_date(self, obj):
        try:
            unix_date = obj.package_entities.get(action=Entity.HARVEST).harvest.harvest_date
            date = unix_to_datetime_tz(unix_date).strftime('%d/%m/%Y') if unix_date else ""
            return {'Harvest date': date}
        except Entity.DoesNotExist:
            return {'Harvest date': ""}

    def get_breaking_date(self, obj):
        try:
            unix_date = obj.package_entities.get(action=Entity.BREAKING).breaking.breaking_date
            date = unix_to_datetime_tz(unix_date).strftime('%d/%m/%Y') if unix_date else ""
            return {'Breaking date': date}
        except Entity.DoesNotExist:
            return {'Breaking date': ""}


class SacPackageSerializer(serializers.ModelSerializer):
    cooperative_name = serializers.SerializerMethodField()
    harvests = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    creation_date = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = (
            'cooperative_name', 'harvests', 'location', 'creation_date',
        )

    def get_cooperative_name(self, obj):
        try:
            user = obj.package_entities.get(action=Entity.BAGGING).user
        except Entity.DoesNotExist:
            return {'Cooperative name': ""}
        company_name = user.company.name if user and user.company else {'Cooperative name': ""}
        return {'Cooperative name': company_name}

    def get_harvests(self, obj):
        pids = ','.join(list(obj.package_harvests.values_list('pid', flat=True)))
        return {'Harvest IDs included': pids}

    def get_location(self, obj):
        try:
            location = obj.package_entities.get(action=Entity.BAGGING).location
        except Entity.DoesNotExist:
            return {'Created location': ""}
        else:
            return {'Created location': "{}, {}".format(location.x, location.y)} \
                if location else {'Created location': ""}

    def get_creation_date(self, obj):
        try:
            unix_date = obj.package_entities.get(action=Entity.BAGGING).timestamp
            creation_date = unix_to_datetime_tz(unix_date).strftime('%d/%m/%Y') if unix_date else ""
        except Entity.DoesNotExist:
            return {'Creation date': ""}
        else:
            return {'Creation date': creation_date}


class LotPackageSerializer(serializers.ModelSerializer):
    sac_ids = serializers.SerializerMethodField()
    transporter = serializers.SerializerMethodField()
    transport_date = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    creation_date = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = (
            'sac_ids', 'transporter', 'location', 'creation_date', 'transport_date'
        )

    def get_sac_ids(self, obj):
        sacs = list(obj.package_sacs.values_list('pid', flat=True).order_by('id'))
        return {'SAC ID included': "{} to {}".format(sacs[0], sacs[-1])} if sacs else {'SAC ID included': ""}

    def get_transporter(self, obj):
        try:
            transporter = obj.package_entities.get(action=Entity.TRANSPORT).transport.transporter
        except Entity.DoesNotExist:
            return {'Organic cocoa transporter': ""}
        return {'Organic cocoa transporter': transporter.name} if transporter else {'Organic cocoa transporter': ""}

    def get_location(self, obj):
        try:
            location = obj.package_entities.get(action=Entity.CREATION).location
        except Entity.DoesNotExist:
            return {'Created location': ""}
        else:
            return {'Created location': "{}, {}".format(location.x, location.y)} \
                if location else {'Created location': ""}

    def get_creation_date(self, obj):
        try:
            unix_date = obj.package_entities.get(action=Entity.CREATION).timestamp
            creation_date = unix_to_datetime_tz(unix_date).strftime('%d/%m/%Y') if unix_date else ""
        except Entity.DoesNotExist:
            return {'Creation date': ""}
        else:
            return {'Creation date': creation_date}

    def get_transport_date(self, obj):
        try:
            unix_date = obj.package_entities.get(action=Entity.TRANSPORT).transport.transport_date
            creation_date = unix_to_datetime_tz(unix_date).strftime('%d/%m/%Y') if unix_date else ""
        except Entity.DoesNotExist:
            return {'Transport date': ""}
        else:
            return {'Transport date': creation_date}


class PackageDetailsSerializer(serializers.ModelSerializer):
    properties = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = ('id', 'pid', 'properties')

    def get_properties(self, obj):
        try:
            properties = getattr(self,
                                 "_{}_properties".format(obj.get_type_display().lower().replace(' ', '_')))
        except AttributeError:
            return ""
        return properties(obj)

    @staticmethod
    def _harvest_properties(obj):
        return HarvestPackageSerializer(obj).data

    @staticmethod
    def _sac_properties(obj):
        return SacPackageSerializer(obj).data

    @staticmethod
    def _lot_properties(obj):
        return LotPackageSerializer(obj).data


class ChainSeriazlier(serializers.ModelSerializer):
    icon_name = serializers.SerializerMethodField()
    action_name = serializers.SerializerMethodField()
    action_short_name = serializers.SerializerMethodField()
    dates = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    class Meta:
        model = Entity
        fields = ('id', 'icon_name', 'action_name', 'action_short_name', 'dates', 'location')

    @staticmethod
    def string_date(unix_date):
        return unix_to_datetime_tz(unix_date).strftime('%d/%m/%Y') if unix_date else ""

    def get_icon_name(self, obj):
        return static("img/{}_icon.svg".format(Entity.CHILD_MODEL_NAMES[obj.action]))

    def get_action_name(self, obj):
        return obj.get_action_display()

    def get_action_short_name(self, obj):
        return obj.action

    def get_dates(self, obj):
        dates = ''
        if obj.action == Entity.HARVEST:
            dates = {
                'harvest': self.string_date(obj.harvest.harvest_date)
            }
        elif obj.action == Entity.BREAKING:
            dates = {
                'breaking': self.string_date(obj.breaking.breaking_date),
                'fermentation': self.string_date(obj.breaking.end_fermentation_date)
            }
        elif obj.action == Entity.HARVEST_RECEPTION:
            dates = {
                'reception': self.string_date(obj.reception.reception_date),
                'transport_date': self.string_date(obj.reception.transport_date),
            }
        elif obj.action == Entity.BAGGING:
            dates = {
                'bagging': self.string_date(obj.timestamp),
            }
        elif obj.action == Entity.HARVEST_RECEPTION:
            dates = {
                'creation': self.string_date(obj.timestamp),
            }
        elif obj.action == Entity.TRANSPORT:
            dates = {
                'transport': self.string_date(obj.transport.transport_date),
            }
        elif obj.action == Entity.LOT_RECEPTION:
            dates = {
                'reception': self.string_date(obj.timestamp),
            }
        return dates

    def get_location(self, obj):
        return "{}, {}".format(obj.location.y, obj.location.x) if obj.location else ''
