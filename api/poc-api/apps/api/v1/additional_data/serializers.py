from rest_framework import serializers

from apps.additional_data.models import (Village, Destination, Parcel, TreeSpecie, OvenType)


class VillageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Village
        fields = ('id', 'name',)


class ParcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = ('id', 'code',)


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ('id', 'name',)


class TreeSpecieSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreeSpecie
        fields = ('id', 'name',)


class OvenTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OvenType
        fields = ('id', 'name', 'oven_height', 'oven_width', 'oven_length', 'type',)

    def validate(self, attrs):
        if attrs.get('type'):
            if attrs['type'] == OvenType.FIXED:
                for key in ('oven_height', 'oven_width', 'oven_length'):
                    if attrs[key] is None:
                        attrs[key] = 1
            else:
                attrs['oven_height'] = None
                attrs['oven_length'] = None
                attrs['oven_width'] = None
        return attrs
