# -*- coding: utf-8 -*-
from django.urls import reverse
from django.test import Client

from ddf import G
from rest_framework import status

from apps.users.models import User, Role
from apps.api.v1.additional_data.tests.tests import MainTestCase


class EntitiesTests(MainTestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()
        self.webpanel_url = reverse('web-panel')
        self.super_user.is_superuser = True
        self.super_user.save()

    def test_web_panel(self):
        response = self.client.get(self.webpanel_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.client.force_login(self.super_user)
        response = self.client.get(self.webpanel_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # TODO: add tests for super user and director roles
        # TODO: for some reason role is not being saved at the moment
