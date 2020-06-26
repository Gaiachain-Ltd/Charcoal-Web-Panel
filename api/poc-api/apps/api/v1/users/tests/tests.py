# -*- coding: utf-8 -*-
from django.urls import reverse
from django.contrib.auth import get_user_model

from ddf import G
from rest_framework import status
from mock import patch

from apps.users.models import Role
from apps.api.v1.additional_data.tests.tests import MainTestCase

User = get_user_model()


class UsersTests(MainTestCase):
    def setUp(self):
        super().setUp()
        self.ping_url = reverse('ping-view')
        self.login_url = reverse('users:login-view')
        self.roles_url = reverse('users:roles')
        self.agents_url = reverse('users:agents')
        self.registration_url = reverse('users:register')

    def test_ping_login_required(self):
        response = self.client.get(self.ping_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ping(self):
        self.client.force_authenticate(self.super_user)
        response = self.client.get(self.ping_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login(self):
        data = {
            'email': 'dont@mail.me',
            'password': 'password'
        }
        response = self.client.post(self.login_url, data, format='json')
        check_data = all([
            k in response.data.keys()
            for k in ['email', 'role', 'refresh', 'access']
        ])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(check_data)

    def test_roles_login_required(self):
        response = self.client.get(self.roles_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_roles(self):
        self.client.force_authenticate(self.super_user)
        response = self.client.get(self.roles_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), Role.objects.count())

    def test_agents_login_required(self):
        response = self.client.get(self.agents_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_agents(self):
        G(User, is_superuser=True)
        self.client.force_authenticate(self.super_user)
        response = self.client.get(self.agents_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), User.objects.count())

    @patch('apps.users.models.User.add_to_chain')
    def test_registration(self, mock_chain):
        self.super_user.is_superuser = True
        self.super_user.save()
        self.client.force_authenticate(self.super_user)
        role, _ = Role.objects.get_or_create(name='SUPER_USER')
        response = self.client.post(self.registration_url, {
            'email': 'test@regist.er',
            'password': 'password',
            'role': role.id,
            'first_name': 'test',
            'last_name': 'test',
            'function': 'KP',
            'contact': '04 08 15 16',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
