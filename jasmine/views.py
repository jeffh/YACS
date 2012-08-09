from django.views.generic import TemplateView
from django.conf import settings


class JasmineView(TemplateView):
    template_name = 'jasmine/jasmine.html'

    def get_context_data(self, **kwargs):
        context = super(JasmineView, self).get_context_data(**kwargs)
        return context
