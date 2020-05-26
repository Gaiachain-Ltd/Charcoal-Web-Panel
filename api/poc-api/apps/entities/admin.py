from django.contrib import admin
from django import forms
from django.contrib.gis.admin import OSMGeoAdmin
from django.contrib.gis.geos import Point

from apps.entities.models import (
    Entity, Package, LoggingBeginning, LoggingEnding, Oven, CarbonizationBeginning, CarbonizationEnding,
    Bag, LoadingTransport, Reception, ReceptionImage
)


class LoggingBeginningInline(admin.StackedInline):
    model = LoggingBeginning


class LoggingEndingInline(admin.StackedInline):
    model = LoggingEnding


class CarbonizationBeginningInline(admin.StackedInline):
    model = CarbonizationBeginning


class CarbonizationEndingInline(admin.StackedInline):
    model = CarbonizationEnding


class EntityInline(admin.StackedInline):
    model = Entity


class PackageAdmin(admin.ModelAdmin):
    model = Package
    inlines = [EntityInline]
    readonly_fields = ("pid",)


class EntityForm(forms.ModelForm):
    latitude = forms.DecimalField(
        min_value=-90,
        max_value=90,
        required=True,
    )
    longitude = forms.DecimalField(
        min_value=-180,
        max_value=180,
        required=True,
    )

    class Meta(object):
        model = Entity
        exclude = []
        # widgets = {'location': forms.HiddenInput()}

    def clean_location(self):
        location = Point(float(self.data['longitude']), float(self.data['latitude']))
        return location

    def __init__(self, *args, **kwargs):
        if args:  # If args exist
            data = args[0].copy()
            if data['latitude'] and data['longitude']:
                latitude = float(data['latitude'])
                longitude = float(data['longitude'])
                data['point'] = Point(longitude, latitude)

        coordinates = kwargs['instance'].location.tuple if 'instance' in kwargs and kwargs['instance'].location else ""
        initial = kwargs.get('initial', {})
        initial['latitude'] = coordinates[1] if coordinates else ""
        initial['longitude'] = coordinates[0] if coordinates else ""
        kwargs['initial'] = initial
        super().__init__(*args, **kwargs)


class EntityAdmin(OSMGeoAdmin):
    inlines = []
    form = EntityForm

    def get_inline_instances(self, request, obj=None):
        self.inlines = []
        possible_inlines = {
            'logging_beginning': LoggingBeginningInline,
            'logging_ending': LoggingEndingInline,
        }
        for f in self.model._meta.get_fields():
            if f.auto_created and not f.concrete and hasattr(obj, f.name) and f.name in possible_inlines:
                self.inlines.append(possible_inlines[f.name])
        return super().get_inline_instances(request, obj=None)


class BagInline(admin.StackedInline):
    model = Bag


class LoadingTransportAdmin(admin.ModelAdmin):
    model = LoadingTransport
    inlines = [BagInline]


admin.site.register(Entity, EntityAdmin)
admin.site.register(LoggingBeginning)
admin.site.register(LoggingEnding)
admin.site.register(CarbonizationBeginning)
admin.site.register(Oven)
admin.site.register(CarbonizationEnding)
admin.site.register(Bag)
admin.site.register(LoadingTransport, LoadingTransportAdmin)
admin.site.register(Reception)
admin.site.register(ReceptionImage)
admin.site.register(Package, PackageAdmin)
