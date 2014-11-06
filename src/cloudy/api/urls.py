from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt

from .views import (PollDeployment, UpdateNodeStatus, DeploymentCommit,
        TriggerRedeploy, EditDeploymentVariables)


urlpatterns = patterns('',
    url(r'^deployments/(?P<key>[0-9a-f]{32})/poll/$',
        csrf_exempt(PollDeployment.as_view()), name='api_poll_deployment'),
    url(r'^deployments/(?P<key>[0-9a-f]{32})/status/$',
        csrf_exempt(UpdateNodeStatus.as_view()),
        name='api_update_node_status'),
    url(r'^deployments/(?P<key>[0-9a-f]{32})/commit/$',
        csrf_exempt(DeploymentCommit.as_view()),
        name='api_deployment_commit'),
    url(r'^deployments/(?P<key>[0-9a-f]{32})/trigger-redeploy/$',
        csrf_exempt(TriggerRedeploy.as_view()),
        name='api_trigger_redeploy'),
    url(r'^deployments/(?P<key>[0-9a-f]{32})/edit-variables/$',
        csrf_exempt(EditDeploymentVariables.as_view()),
        name='api_edit_deployment_variables'),
)
