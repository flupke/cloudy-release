from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt

from .views import PollDeployment, UpdateNodeStatus


urlpatterns = patterns('',
    url(r'^deployment/(?P<key>[0-9a-f]{32})/poll/$',
        csrf_exempt(PollDeployment.as_view()), name='api_poll_deployment'),
    url(r'^deployment/(?P<key>[0-9a-f]{32})/status/$',
        csrf_exempt(UpdateNodeStatus.as_view()),
        name='api_update_node_status'),
)
