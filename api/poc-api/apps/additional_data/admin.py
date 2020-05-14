from io import StringIO
import csv

from django.contrib import admin
from django.urls import path
from django.db import transaction, IntegrityError
from django.http.response import Http404
from django.shortcuts import render

from apps.additional_data.models import (
    Village, Destination, Parcel, TreeSpecie, OvenType
)


admin.site.register(Village)
admin.site.register(Destination)
admin.site.register(Parcel)
admin.site.register(TreeSpecie)
admin.site.register(OvenType)
