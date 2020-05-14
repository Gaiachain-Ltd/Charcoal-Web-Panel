# -*- coding: utf-8 -*-
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status

from apps.users.models import Role
from apps.additional_data.tests.tests import MainTestCase

User = get_user_model()


class UsersTests(MainTestCase):
    def setUp(self):
        super().setUp()
        self.ping_url = reverse('ping-view')
        self.login_url = reverse('users:login-view')
        self.roles_url = reverse('users:roles')
        self.agents_url = reverse('users:agents')

    def test_ping(self):
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

    def test_roles(self):
        response = self.client.get(self.roles_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), Role.objects.count())

    def test_agents(self):
        response = self.client.get(self.agents_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), User.objects.count())
