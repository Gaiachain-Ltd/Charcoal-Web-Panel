from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient

from apps.users.tests.factories import (UserFactory)
from apps.users.models import Role
from apps.additional_data.tests.factories import (
    VillageFactory, ParcelFactory, DestinationFactory
)
from apps.additional_data.models import (
    Village, Parcel, Destination
)


SUPER_ROLE, _ = Role.objects.get_or_create(name='SUPER_USER')


class MainTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.super_user = UserFactory(email='dont@mail.me', role=SUPER_ROLE)
        self.village = VillageFactory()
        self.parcel = ParcelFactory()
        self.destination = DestinationFactory()


class AdditionalDataTests(MainTestCase):
    def setUp(self):
        super().setUp()
        self.destinations_url = reverse('additional_data:additional-data-destinations')
        self.villages_url = reverse('additional_data:additional-data-villages')
        self.parcels_url = reverse('additional_data:additional-data-parcels')
        self.all_data_url = reverse('additional_data:additional-data-all-data')

    def test_destinations(self):
        response = self.client.get(self.destinations_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Destination.objects.count())

    def test_villages(self):
        response = self.client.get(self.villages_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Village.objects.count())

    def test_parcels(self):
        response = self.client.get(self.parcels_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Parcel.objects.count())

    def test_all_data(self):
        response = self.client.get(self.all_data_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_data = all([
            k in response.data.keys()
            for k in ['tree_species', 'oven_types', 'villages', 'parcels', 'destinations']
        ])
        self.assertTrue(check_data)
