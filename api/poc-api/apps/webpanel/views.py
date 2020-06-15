from django.views.generic import TemplateView
from django.conf import settings


class WebPanelView(TemplateView):
    template_name = 'main.html'

    def get_context_data(self, **kwargs):
        kwargs['mapbox_token'] = settings.MAPBOX_TOKEN
        return super().get_context_data(**kwargs)
