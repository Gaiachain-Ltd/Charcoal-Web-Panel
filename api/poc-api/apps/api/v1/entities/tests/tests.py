import json
import random
import string

from django.urls import reverse
from django.contrib.auth import get_user_model

from ddf import G
from mock import patch
from rest_framework import status

from apps.entities.models import (
    Entity, Package, Replantation, LoggingEnding
)
from apps.api.v1.additional_data.tests.tests import MainTestCase

User = get_user_model()


def random_pid(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


PLOT_PID = f'AM003PM/{random_pid()}/04-03-2020'
LOT_QR_CODE = random_pid()


class EntitiesTests(MainTestCase):
    def setUp(self):
        super().setUp()
        self.entity_create_url = reverse('entities:entities-new')
        self.entities_list_url = reverse('entities:entities-list')
        self.harvests_url = reverse('entities:entities-harvests')
        self.plots_url = reverse('entities:entities-plots')
        self.replantation_list_url = reverse('entities:replantation-list')
        self.replantation_plots_url = reverse('entities:replantation-plots')
        self.super_user.is_superuser = True
        self.super_user.save()
        self.location = {"latitude": 0.0, "longitude": 0.0}

    def create_entity(self, action_type):
        data = {
            'timestamp': 1576181866,
            'action': action_type,
            'location': self.location
        }
        return data


    def create_logging_beginning(self):
        data = self.create_entity(action_type=Entity.LOGGING_BEGINNING)
        data['pid'] = PLOT_PID
        data['properties'] = {
            "tree_specie": self.tree_specie.id,
            "village": self.village.id,
            "parcel": self.parcel.id,
            "beginning_date": 1576181866
        }
        return self.client.post(self.entity_create_url, data, format='json')

    def create_logging_ending(self, pid):
        data = self.create_entity(action_type=Entity.LOGGING_ENDING)
        data['pid'] = pid
        data['properties'] = {"number_of_trees": 1, "ending_date": 1576181866}
        return self.client.post(self.entity_create_url, data, format='json')

    def create_carbonization_beginning(self):
        plot_response = self.create_logging_beginning()
        data = self.create_entity(action_type=Entity.CARBONIZATION_BEGINNING)
        data['pid'] = f'{plot_response.data["pid"]}/AM004PM'
        data['properties'] = {
            "oven_type": self.oven_type.id,
            "beginning_date": 1576181866,
            "oven_id": "A"
        }
        data['location'] = json.dumps(data['location'])
        return self.client.post(self.entity_create_url, data, format='json')

    def create_carbonization_ending(self, pid):
        data = self.create_entity(action_type=Entity.CARBONIZATION_ENDING)
        data['pid'] = pid
        data['properties'] = {"oven_id": "A", "end_date": 1576181866}
        return self.client.post(self.entity_create_url, data, format='json')

    def create_transport(self):
        harvest_response = self.create_carbonization_beginning()
        data = self.create_entity(action_type=Entity.LOADING_TRANSPORT)
        data['pid'] = f'{harvest_response.data["pid"]}/AM004PM/12345AB67/T1/31-03-2020'
        data['properties'] = {
            "bags_qr_codes": ["123-321"],
            "loading_date": 1576181866,
            "destination": self.destination.id,
            "plate_number": "12345AB67"
        }
        return self.client.post(self.entity_create_url, data, format='json')

    def create_reception(self):
        data = self.create_entity(action_type=Entity.RECEPTION)
        data['properties'] = {
            "bags_qr_codes": ["123-321"],
            "reception_date": 1576181866
        }
        return self.client.post(self.entity_create_url, data, format='json')

    def test_create_plot_login_required(self):
        response = self.create_logging_beginning()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('apps.entities.models.Package.add_to_chain')
    @patch('apps.entities.models.Entity.update_in_chain')
    def test_create_plot(self, mock_chain, mock_chain2):
        self.client.force_authenticate(self.super_user)
        response = self.create_logging_beginning()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pid', response.data)

        response = self.create_logging_ending(response.data['pid'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pid', response.data)

    @patch('apps.entities.models.Package.add_to_chain')
    @patch('apps.entities.models.Entity.update_in_chain')
    def test_create_harvest(self, mock_chain, mock_chain2):
        self.client.force_authenticate(self.super_user)
        response = self.create_carbonization_beginning()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pid', response.data)

        response = self.create_carbonization_ending(response.data['pid'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pid', response.data)

    @patch('apps.entities.models.Package.add_to_chain')
    @patch('apps.entities.models.Entity.update_in_chain')
    def test_create_transport(self, mock_chain, mock_chain2):
        self.client.force_authenticate(self.super_user)
        response = self.create_transport()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pid', response.data)

        response = self.create_reception()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pid', response.data)

    def test_utils(self):
        from datetime import datetime
        from apps.api.v1.entities.utils import unix_to_datetime_tz
        dt = unix_to_datetime_tz(1)
        self.assertIsInstance(dt, datetime)
        dt = unix_to_datetime_tz(0)
        self.assertIsNone(dt)

    @patch('apps.entities.models.Package.add_to_chain')
    def test_entities_list(self, mock_chain):
        self.client.force_authenticate(self.super_user)
        self.create_transport()
        response = self.client.get(self.entities_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Entity.objects.count())

    @patch('apps.entities.models.Package.add_to_chain')
    def test_plots(self, mock_chain):
        self.client.force_authenticate(self.super_user)
        self.create_logging_beginning()
        last_action = 'LB'
        harvests_url = "{}?last_action={}".format(self.plots_url, last_action)
        response = self.client.get(harvests_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Package.objects.filter(last_action__action=last_action).count())

    @patch('apps.entities.models.Package.add_to_chain')
    def test_harvests(self, mock_chain):
        self.client.force_authenticate(self.super_user)
        self.create_carbonization_beginning()
        last_action = 'CB'
        harvests_url = "{}?last_action={}".format(self.harvests_url, last_action)
        response = self.client.get(harvests_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Package.objects.filter(last_action__action=last_action).count())

    @patch('apps.api.v1.entities.serializers.ReplantationListSerializer.get_blockchain_details', return_value={})
    def test_replantation_list_login_required(self, mock1):
        response = self.client.get(self.replantation_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('apps.entities.models.Replantation.add_to_chain')
    @patch('apps.entities.models.Package.add_to_chain')
    @patch('apps.api.v1.entities.serializers.ReplantationListSerializer.get_blockchain_details', return_value={})
    def test_replantation_list(self, mock_chain, mock_chain2, mock3):
        G(Replantation)
        self.client.force_authenticate(self.super_user)
        response = self.client.get(self.replantation_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        replantation_count = Replantation.objects.all().count()
        self.assertEqual(response.data['count'], replantation_count)

        plot_response = self.create_carbonization_beginning()
        response = self.client.post(self.replantation_list_url, {
            "trees_planted": 1,
            "beginning_date": 1576181866,
            "ending_date": 1576181866,
            "location": self.location,
            "plot": plot_response.data['package_id'],
            "tree_specie": self.tree_specie.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(replantation_count + 1, Replantation.objects.all().count())

    def test_replantation_plots_login_required(self):
        response = self.client.get(self.replantation_plots_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_replantation_plots(self):
        # create new plot with LoggingEnding and create a replantation entry for it
        package = G(Package, type=Package.PLOT)
        entity = G(Entity, package=package, action='LE')
        G(LoggingEnding, entity=entity)
        G(Replantation, plot=package)
        package.last_action = entity
        package.save()

        # create new plot with LoggingEnding without a replantation entry
        package = G(Package, type=Package.PLOT)
        entity = G(Entity, package=package, action='LE')
        G(LoggingEnding, entity=entity)
        package.last_action = entity
        package.save()
        self.client.force_authenticate(self.super_user)
        response = self.client.get(self.replantation_plots_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
