import json
import datetime

from django.views.generic import View
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict

from ..projects.models import Deployment, Node


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


class DeploymentView(ApiView):
    '''
    Base class for deployment views.
    '''

    model = Deployment
    object_attr = 'deployment'


class PollDeployment(DeploymentView):
    '''
    Clients regularly poll this view to retrieve deployment state.        

    :param node_name: the client node name
    '''

    required_parameters = ['node_name']

    def get(self, request, *args, **kwargs):
        # Get or create Node object
        node_name = request.GET['node_name']
        node, _ = Node.objects.get_or_create(deployment=self.deployment,
                name=node_name)
        # Build response dict
        data = model_to_dict(self.deployment.project)
        data.update(model_to_dict(self.deployment))
        del data['project']
        del data['owner']
        del data['id']
        data['commit'] = self.deployment.actual_commit()
        data['deployment_hash'] = self.deployment.hash()
        data['source_url'] = self.deployment.source_url()
        data['update_status_url'] = request.build_absolute_uri(
                reverse('api_update_node_status',
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
    '''

    required_parameters = ['node_name', 'status', 'source_url']

    def post(self, request, *args, **kwargs):
        # Get Node object
        node_name = request.POST['node_name']
        node = get_object_or_404(Node, deployment=self.deployment,
                name=node_name)

        # Update node attributes
        attrs = {}
        status = request.POST['status']
        now = datetime.datetime.now()
        try:
            if status == 'success' or status == 'error':
                attrs['last_deployment_output'] = request.POST['output']
                attrs['last_deployment_date'] = now
            elif status != 'pending':
                return HttpResponseBadRequest('invalid status: %s' % status)
        except KeyError as exc:
            return HttpResponseBadRequest('missing parameter: %s' % exc)
        attrs['last_deployment_status'] = status
        attrs['last_deployed_source_url'] = request.POST['source_url']
        node.__dict__.update(attrs)
        node.save()
        return 'OK'

