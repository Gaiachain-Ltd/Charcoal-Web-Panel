from django.db import models
from django.utils.translation import ugettext_lazy as _


class BaseAdditionalModel(models.Model):
    name_field_verbose_name = _('Name')
    name = models.CharField(verbose_name=_('Name'), max_length=100, unique=True)
    active = models.BooleanField(verbose_name=_('Active'), default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._meta.get_field('name').verbose_name = self.name_field_verbose_name


class Village(BaseAdditionalModel):
    name_field_verbose_name = _('Village name')


class Parcel(BaseAdditionalModel):
    name_field_verbose_name = _('Parcel code')


class Destination(BaseAdditionalModel):
    pass


class TreeSpecie(BaseAdditionalModel):
    pass


class OvenType(BaseAdditionalModel):
    CUSTOM = 1
    FIXED = 2
    TYPE_CHOICES = (
        (CUSTOM, _('Custom')),
        (FIXED, _('Fixed')),
    )
    type = models.PositiveSmallIntegerField(default=CUSTOM, choices=TYPE_CHOICES)
    oven_height = models.PositiveIntegerField(verbose_name=_('Oven height'), null=True, blank=True)
    oven_width = models.PositiveIntegerField(verbose_name=_('Oven width'), null=True, blank=True)
    oven_length = models.PositiveIntegerField(verbose_name=_('Oven length'), null=True, blank=True)

    def __str__(self):
        return self.name
