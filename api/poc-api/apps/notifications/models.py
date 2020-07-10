# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.entities.models import Package


class Notification(models.Model):
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, verbose_name=_('Users'),
        related_name='notifications'
    )
    read_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, verbose_name=_('Read by'),
        related_name='read_notifications', blank=True
    )
    package = models.ForeignKey(
        Package, verbose_name=_('Package'), on_delete=models.CASCADE,
        related_name='notifications'
    )
    action_name = models.CharField(verbose_name=_('Action name'), max_length=12)
