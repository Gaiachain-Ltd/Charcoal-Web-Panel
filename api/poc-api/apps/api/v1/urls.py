# -*- coding: utf-8 -*-
from django.urls import path, include

from apps.api.v1.users.views import PingAPIView
from config.swagger_schema import schema_view


urlpatterns = [
    path('info/', schema_view),
    path('ping/', PingAPIView.as_view(), name='ping-view'),
    path('auth/', include('apps.api.v1.users.urls')),
    path('additional_data/', include('apps.api.v1.additional_data.urls')),
    path('entities/', include('apps.api.v1.entities.urls')),
]
