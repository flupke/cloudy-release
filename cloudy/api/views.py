import json

from django.views.generic import View
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from django.utils import timezone

from ..projects.models import Deployment, Node, DeploymentLogEntry


class ApiView(View):
    '''
    Base class for all API views.
    '''

    model = None
    object_attr = None
    required_parameters = []

    def dispatch(self, request, key, *args, **kwargs):
        # Get the main object from key in request path
        obj = get_object_or_404(self.model, key=key)
        setattr(self, self.object_attr, obj)

        # Validate request parameters
        if request.method == 'GET':
            request_parameters = set(request.GET)
        elif request.method == 'POST':
            request_parameters = set(request.POST)
        else:
            return HttpResponseBadRequest('%s HTTP method not supported '
                    'by this view')
        required_parameters = set(self.required_parameters)
        missing_parameters = required_parameters.difference(
                request_parameters)
        unknown_parameters = request_parameters.difference(request_parameters)
        errors = []
        if missing_parameters:
            errors.append('missing parameters: %s' % 
                    ', '.join(missing_parameters))
        if unknown_parameters:
            errors.append('unkown parameters: %s' % 
                    ', '.join(unknown_parameters))
        if errors:
            return HttpResponseBadRequest('\n'.join(errors))

        # Run the request handler, convert response to JSON if necessary
        response = super(ApiView, self).dispatch(request, *args, **kwargs)
        if not isinstance(response, HttpResponse):
            response = HttpResponse(json.dumps(response),
                    content_type='application/json')
        return response

# ----------------------------------------------------------------------------
# Deployments

class DeploymentView(ApiView):
    '''
    Base class for deployment views.
    '''

    model = Deployment
    object_attr = 'deployment'


class PollDeployment(DeploymentView):
    '''
    Clients regularly poll this view to retrieve deployment state.        

    :param node_name: 
        the client node name, creates a new node if there was not already a
        node in this deployment with this name
    '''

    def get(self, request, *args, **kwargs):
        # Get or create Node object if node_name was passed in the URL
        if 'node_name' in request.GET:
            node_name = request.GET['node_name']
            Node.objects.get_or_create(deployment=self.deployment,
                    name=node_name)
        # Build response dict
        data = model_to_dict(self.deployment.project)
        data.update(model_to_dict(self.deployment))
        del data['project']
        del data['owner']
        del data['id']
        del data['name']
        if self.deployment.base_variables is not None:
            data['base_variables_format'] = self.deployment.base_variables.variables_format
            data['base_variables'] = self.deployment.base_variables.variables
        else:
            data['base_variables_format'] = None
            data['base_variables'] = None
        data['project_name'] = self.deployment.project.name
        data['deployment_name'] = self.deployment.name
        data['commit'] = self.deployment.commit
        data['deployment_hash'] = self.deployment.hash()
        data['source_url'] = self.deployment.source_url()
        data['update_status_url'] = request.build_absolute_uri(
                reverse('api_update_node_status',
                kwargs={'key': self.deployment.key}))
        data['commit_url'] = request.build_absolute_uri(
                reverse('api_deployment_commit', 
                kwargs={'key': self.deployment.key}))
        return data


class UpdateNodeStatus(DeploymentView):
    '''
    Used by clients to POST updates on their status.

    :param node_name: the client node name
    :param status: the status string
    :param source_url: 
        the "source_url" value that was returned by the poll view
    :param output: 
        the console output of the deployment; only required for "success" or
        "error" status
    :param client_version:
        the cloudy release client version used on the node
    '''

    required_parameters = ['node_name', 'status', 'source_url',
            'client_version']

    def post(self, request, *args, **kwargs):
        # Get Node object
        node_name = request.POST['node_name']
        source_url = request.POST['source_url']
        node = get_object_or_404(Node, deployment=self.deployment,
                name=node_name)

        # Update node attributes
        attrs = {}
        status = request.POST['status']
        now = timezone.now()
        try:
            if status == 'success' or status == 'error':
                output = request.POST['output']
                attrs['last_deployment_output'] = output
                attrs['last_deployment_date'] = now
            elif status != 'pending':
                return HttpResponseBadRequest('invalid status: %s' % status)
            else:
                output = None
        except KeyError as exc:
            return HttpResponseBadRequest('missing parameter: %s' % exc)
        attrs['last_deployment_status'] = status
        attrs['last_deployed_source_url'] = source_url
        attrs['client_version'] = request.POST['client_version']
        node.__dict__.update(attrs)
        node.save()

        # Add log entry
        DeploymentLogEntry.objects.create(node=node, source_url=source_url,
                type='deployment.%s' % status, text=output)

        return 'OK'


class DeploymentCommit(DeploymentView):
    '''
    Used to retrieve or update a deployment's commit.
    '''

    def get(self, request, *args, **kwargs):
        return self.deployment.commit
    
    def post(self, request, *args, **kwargs):
        try:
            commit = request.POST['commit']
        except KeyError:
            return HttpResponseBadRequest('missing parameter: commit')
        self.deployment.commit = commit
        self.deployment.save()
        return 'OK'


class TriggerRedeploy(DeploymentView):
    '''
    Used to trigger a redeploy.
    '''

    def post(self, request, *args, **kwargs):
        self.deployment.trigger_redeploy()
        return 'OK'
