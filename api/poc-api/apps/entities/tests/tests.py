import random
import string

from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status

from apps.entities.models import (
    Entity, Package
)
from apps.additional_data.tests.tests import MainTestCase

User = get_user_model()


def random_pid(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


HARVEST_PID = random_pid()
LOT_QR_CODE = random_pid()


class EntitiesTests(MainTestCase):
    def setUp(self):
        super().setUp()
        self.entity_create_url = reverse('entities-new')
        self.lots_url = reverse('entities-lots')
        self.entities_list_url = reverse('entities-list')
        self.batch_url = reverse('entities-batch')
        self.harvests_url = reverse('entities-harvests')
        self.relations_list = reverse('relations-batch')
        self.client.login(email='dont@mail.me', password='password')

    def create_entity(self, action_type):
        data = {
            'timestamp': 1576181866,
            'action': action_type,
            'user': self.super_user.id,
        }
        return data

    def create_harvest(self):
        data = self.create_entity(action_type=Entity.HARVEST)
        data['pid'] = HARVEST_PID
        data['properties'] = {
            'parcel': self.parcel.id,
            'harvest_date': 1576181866
        }
        return self.client.post(self.entity_create_url, data, format='json')

    def create_breaking(self):
        harvest_response = self.create_harvest()
        data = self.create_entity(action_type=Entity.BREAKING)
        data['pid'] = harvest_response.data['pid']
        data['properties'] = {
            'breaking_date': 1576181866,
            'end_fermentation_date': 1576181866,
            'beans_volume': 777
        }
        return self.client.post(self.entity_create_url, data, format='json')

    def create_reception(self):
        breaking_response = self.create_breaking()
        data = self.create_entity(action_type=Entity.HARVEST_RECEPTION)
        data['pid'] = breaking_response.data['pid']
        data['properties'] = {
            'reception_date': 1576181866,
            'transport_date': 1576181866,
            'buyer': self.company.id
        }
        return self.client.post(self.entity_create_url, data, format='json')

    def create_initial_lot(self):
        return self.client.post(self.lots_url)

    def create_bagging(self):
        reception_response = self.create_reception()
        harvest_package = Package.objects.get(pid=reception_response.data['pid'])
        data = self.create_entity(action_type=Entity.BAGGING)
        initial_lot = self.create_initial_lot().data['pid']
        data['pid'] = reception_response.data['pid']
        data['properties'] = {
            'lot_pid': initial_lot,
            'harvest_weights': [{
                'pid': harvest_package.pid,
                'weight': harvest_package.weight
            }]
        }
        return self.client.post(self.entity_create_url, data, format='json')

    def create_lot(self):
        lot_response = self.create_initial_lot()
        data = self.create_entity(action_type=Entity.CREATION)
        data['pid'] = lot_response.data['pid']
        data['qr_code'] = LOT_QR_CODE
        data['properties'] = {
            'notes': 'some notes'
        }
        return self.client.post(self.entity_create_url, data, format='json')

    def create_transport(self):
        self.create_lot()
        data = self.create_entity(action_type=Entity.TRANSPORT)
        data['qr_code'] = LOT_QR_CODE
        data['properties'] = {
            'transporter': self.company.id,
            'transport_date': 1576181866,
            'destination': self.destination.id
        }
        return self.client.post(self.entity_create_url, data, format='json')

    def create_lot_reception(self):
        self.create_transport()
        data = self.create_entity(action_type=Entity.LOT_RECEPTION)
        data['qr_code'] = LOT_QR_CODE
        data['properties'] = {
            'weight': 777,
        }
        return self.client.post(self.entity_create_url, data, format='json')

    def test_create_harvest(self):
        response = self.create_harvest()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pid', response.data)

    def test_create_breaking(self):
        response = self.create_breaking()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pid', response.data)

    def test_create_reception(self):
        response = self.create_reception()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pid', response.data)

    def test_create_initial_lot(self):
        response = self.create_initial_lot()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pid', response.data)

    def test_unused_lots(self):
        self.create_initial_lot()
        response = self.client.get(self.lots_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Package.objects.filter(type=Package.LOT).count())

    def test_create_bagging(self):
        response = self.create_bagging()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pid', response.data)

    def test_lot_creation(self):
        response = self.create_lot()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pid', response.data)

    def test_create_transport(self):
        response = self.create_transport()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pid', response.data)

    def test_create_lot_reception(self):
        response = self.create_transport()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pid', response.data)

    def test_entities_list(self):
        self.create_lot_reception()
        response = self.client.get(self.entities_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Entity.objects.count())

    def test_entities_batch(self):
        self.create_lot_reception()
        data = {
            'pid': [e.package.pid for e in Entity.objects.all()]
        }
        response = self.client.post(self.batch_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Entity.objects.count())

    def test_get_pid(self):
        self.create_lot_reception()
        package = Package.objects.first()
        response = self.client.get(
            reverse('entities-get-pid', kwargs={'pk': package.qr_code})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, package.pid)

    def test_harvests(self):
        self.create_harvest()
        last_action = 'HA'
        harvests_url = "{}?last_action={}".format(self.harvests_url, last_action)
        response = self.client.get(harvests_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Package.objects.filter(last_action__action=last_action).count())

    def test_relations_batch(self):
        self.create_lot_reception()
        data = {
            'pids': [e.pid for e in Package.objects.all()]
        }
        response = self.client.post(self.relations_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Package.objects.count())
