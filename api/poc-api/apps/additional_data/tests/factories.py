# -*- coding: utf-8 -*-
import factory


class VillageFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'village-{0}'.format(n))

    class Meta:
        model = 'additional_data.Village'
        django_get_or_create = ('name',)


class ParcelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'additional_data.Parcel'


class DestinationFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'destination-{0}'.format(n))

    class Meta:
        model = 'additional_data.Destination'


class OvenTypeFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'oven-type-{0}'.format(n))

    class Meta:
        model = 'additional_data.OvenType'


class TreeSpecieFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'tree-specie-{0}'.format(n))

    class Meta:
        model = 'additional_data.TreeSpecie'
