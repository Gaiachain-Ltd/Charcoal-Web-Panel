from django.views.generic import TemplateView


class WebPanelView(TemplateView):
    template_name = 'main.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['company_name'] = self.request.user.company.name\
            if self.request.user.is_authenticated and self.request.user.company else ""
        return ctx
