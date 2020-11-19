from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404

from .models import AppPackage


class WebPanelView(TemplateView):
    template_name = 'main.html'

    def dispatch(self, request, *args, **kwargs):
        if bool(request.user and request.user.is_authenticated) and (
                request.user.is_superuser_role or request.user.is_director):
            return super().dispatch(request, *args, **kwargs)
        raise Http404

    def get_context_data(self, **kwargs):
        kwargs['mapbox_token'] = settings.MAPBOX_TOKEN
        kwargs['app_package'] = AppPackage.objects.first()
        return super().get_context_data(**kwargs)
