"""poc_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import RedirectView

from apps.users.views import PingAPIView
from apps.webpanel.views import WebPanelView
from config.swagger_schema import schema_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/info/', schema_view),
    path('ping/', PingAPIView.as_view(), name='ping-view'),
    path('auth/', include('apps.users.urls')),
    path('additional_data/', include('apps.additional_data.urls')),
    path('blockchain/', include('apps.blockchain.urls')),
    path('entities/', include('apps.entities.urls')),
    path('accounts/', include('allauth.urls')),
    path('web_panel/', view=WebPanelView.as_view(), name='web-panel'),
    path('', view=RedirectView.as_view(url=reverse_lazy('account_login')), name='main-url'),
]\
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) +\
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
