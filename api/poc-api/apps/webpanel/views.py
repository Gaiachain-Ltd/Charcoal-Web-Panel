from django.views.generic import TemplateView


class WebPanelView(TemplateView):
    template_name = 'main.html'
