# -*- coding: utf-8 -*-
from .base import *

POSTGIS_HOST = env('POSTGIS_HOST', default='')
DATABASES = {
    'default': env.db('DATABASE_URL', default='django.contrib.gis.db.backends.postgis://poc_api_user:poc_api_db_1024@{}:5432/poc_api_db'.format(POSTGIS_HOST)),
}