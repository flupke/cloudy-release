from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


class DashboardView(TemplateView):

    template_name = 'cloudy/dashboard.html'

    def get(self, request):
        return self.render_to_response({})

