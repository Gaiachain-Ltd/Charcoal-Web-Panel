from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient

from apps.users.tests.factories import (UserFactory)
from apps.users.models import Role
from apps.additional_data.tests.factories import (
    VillageFactory, ParcelFactory, DestinationFactory, TreeSpecieFactory, OvenTypeFactory
)
from apps.additional_data.models import (
    Village, Parcel, Destination, TreeSpecie, OvenType
)


class MainTestCase(APITestCase):
    def setUp(self):
        SUPER_ROLE, _ = Role.objects.get_or_create(name='SUPER_USER')
        self.client = APIClient()
        self.super_user = UserFactory(email='dont@mail.me', role=SUPER_ROLE)
        self.village = VillageFactory()
        self.parcel = ParcelFactory()
        self.destination = DestinationFactory()
        self.oven_type = OvenTypeFactory()
        self.tree_specie = TreeSpecieFactory()


class AdditionalDataTests(MainTestCase):
    def setUp(self):
        super().setUp()
        self.destinations_list_url = reverse('additional_data:destinations-list')
        self.villages_list_url = reverse('additional_data:villages-list')
        self.parcels_list_url = reverse('additional_data:parcels-list')
        self.tree_species_list_url = reverse('additional_data:tree-species-list')
        self.oven_types_list_url = reverse('additional_data:oven-types-list')
        self.all_data_url = reverse('additional_data:additional-data-all-data')

    def test_destinations_login_required(self):
        response = self.client.get(self.destinations_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_destinations_list(self):
        self.client.force_authenticate(self.super_user)
        response = self.client.get(self.destinations_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Destination.objects.count())

    def test_villages_login_required(self):
        response = self.client.get(self.villages_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_villages_list(self):
        self.client.force_authenticate(self.super_user)
        response = self.client.get(self.villages_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Village.objects.count())

    def test_parcels_login_required(self):
        response = self.client.get(self.parcels_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_parcels_list(self):
        self.client.force_authenticate(self.super_user)
        response = self.client.get(self.parcels_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Parcel.objects.count())

    def test_tree_species_login_required(self):
        response = self.client.get(self.tree_species_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_tree_species_list(self):
        self.client.force_authenticate(self.super_user)
        response = self.client.get(self.tree_species_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], TreeSpecie.objects.count())

    def test_oven_types_login_required(self):
        response = self.client.get(self.oven_types_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_oven_types_list(self):
        self.client.force_authenticate(self.super_user)
        response = self.client.get(self.oven_types_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], OvenType.objects.count())

    def test_all_data_login_required(self):
        response = self.client.get(self.all_data_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_data(self):
        self.client.force_authenticate(self.super_user)
        response = self.client.get(self.all_data_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_data = all([
            k in response.data.keys()
            for k in ['tree_species', 'oven_types', 'villages', 'parcels', 'destinations']
        ])
        self.assertTrue(check_data)
