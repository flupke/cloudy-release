import json
import collections

from django.views.generic import View
from django.http import (HttpResponse, HttpResponseBadRequest,
        HttpResponseForbidden)
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from django.utils import timezone

from ..projects.models import Deployment, Node, DeploymentLogEntry
from ..projects.exceptions import InvalidOperation
from ..projects import varops
from ..users.models import UserProfile
from ..logs import add_log


class ApiView(View):
    '''
    Base class for all API views.
    '''

    model = None
    object_attr = None
    required_parameters = []
    operation = None

    def dispatch(self, request, key, *args, **kwargs):
        # Get the main object from key in request path
        obj = get_object_or_404(self.model, key=key)
        setattr(self, self.object_attr, obj)

        # Validate request parameters
        if request.method == 'GET':
            params = request.GET
            request_parameters = set(request.GET)
        elif request.method == 'POST':
            params = request.POST
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

        # Check access
        if hasattr(obj, 'can_do'):
            # Get secret from request parameters or headers
            if self.operation is None:
                raise Exception('subclasses of ApiView accessing objects with '
                        'ACLs must define the "operation" attribute')
            if isinstance(self.operation, collections.Mapping):
                operation = self.operation[request.method]
            else:
                operation = self.operation
            if 'HTTP_AUTHORIZATION' in request.META:
                _, _, secret = request.META['HTTP_AUTHORIZATION'].partition(' ')
            else:
                secret = params.get('secret')

            # Retrieve user
            try:
                profile = UserProfile.objects.get(secret=secret)
                self.user = profile.user
            except UserProfile.DoesNotExist:
                self.user = None

            # Check ACL
            if not obj.can_do(self.user, operation):
                return HttpResponseForbidden('access denied')

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

    operation = 'read'

    def get(self, request, *args, **kwargs):
        # Get or create Node object if node_name was passed in the URL
        if 'node_name' in request.GET:
            node_name = request.GET['node_name']
            node, created = Node.objects.get_or_create(
                    deployment=self.deployment, name=node_name)
            if not created:
                node.last_seen = timezone.now()
                node.save(update_fields=['last_seen'])
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
        data['clean'] = self.deployment.project.clean_repository
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
    operation = 'read'

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

    operation = {
        'GET': 'read',
        'POST': 'write',
    }

    def get(self, request, *args, **kwargs):
        return self.deployment.commit

    def post(self, request, *args, **kwargs):
        try:
            commit = request.POST['commit']
        except KeyError:
            return HttpResponseBadRequest('missing parameter: commit')
        if self.deployment.commit != commit:
            add_log('{user} deployed {project}/{deployment}@{commit}',
                    project=self.deployment.project,
                    deployment=self.deployment, commit=commit, user=self.user,
                    object=self.deployment)
        self.deployment.commit = commit
        self.deployment.save()
        return 'OK'


class TriggerRedeploy(DeploymentView):
    '''
    Used to trigger a redeploy.
    '''

    operation = 'write'

    def post(self, request, *args, **kwargs):
        self.deployment.trigger_redeploy()
        add_log('{user} triggered a redeploy for {project}/{deployment}',
                project=self.deployment.project, deployment=self.deployment,
                user=self.user, object=self.deployment)
        return 'OK'


class EditDeploymentVariables(DeploymentView):
    '''
    Modify deployment variables.

    :param operation: the edit operation. Supported operations are:
        * set_add
        * set_discard
    :param path: target of the edition in deployment variables dict
    :param value: the json-encoded value passed to the operation
    '''

    required_parameters = ['operation', 'path', 'value']
    valid_operations = set(['set_add', 'set_discard'])
    operation = 'write'

    def post(self, request, *args, **kwargs):
        operation = request.POST['operation']
        path = request.POST['path']
        value = request.POST['value']

        # Validate parameters
        if operation not in self.valid_operations:
            return 'invalid operation: %s' % operation
        try:
            value = json.loads(value)
        except:
            return 'the "value" parameter is not valid JSON'

        # Apply edit and save it to the model
        try:
            vars_dict = self.deployment.vars_dict()
        except InvalidOperation:
            return 'deployment variales do not contain a dict and '\
                    'cannot be edited'
        operation_func = getattr(varops, operation)
        try:
            operation_func(vars_dict, path, value)
        except KeyError:
            return 'invalid path: %s' % path
        self.deployment.set_vars_from_dict(vars_dict)
        self.deployment.save(update_fields=['variables'])

        add_log('{user} edited {project}/{deployment} deployment variables',
                project=self.deployment.project, deployment=self.deployment,
                user=self.user, object=self.deployment)

        return 'OK'
