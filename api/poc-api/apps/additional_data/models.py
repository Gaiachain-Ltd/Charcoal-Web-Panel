from django.db import models
from django.utils.translation import ugettext_lazy as _


class Village(models.Model):
    name = models.CharField(verbose_name=_('Village name'), max_length=100)

    def __str__(self):
        return self.name


class Parcel(models.Model):
    code = models.CharField(verbose_name=_('Parcel code'), null=True, max_length=20)

    def __str__(self):
        return self.code


class Destination(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=100)

    def __str__(self):
        return self.name


class TreeSpecie(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=100)

    def __str__(self):
        return self.name


class OvenType(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=20)
    oven_height = models.PositiveIntegerField(verbose_name=_('Oven height'), null=True, blank=True)
    oven_width = models.PositiveIntegerField(verbose_name=_('Oven width'), null=True, blank=True)
    oven_length = models.PositiveIntegerField(verbose_name=_('Oven length'), null=True, blank=True)

    def __str__(self):
        return self.name
