import json

from django.views.generic import View
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict

from ..projects.models import Deployment, Node


class ApiView(View):
    '''
    Base class for all API views.
    '''

    model = None
    object_attr = None

    def dispatch(self, request, key, *args, **kwargs):
        obj = get_object_or_404(self.model, key=key)
        setattr(self, self.object_attr, obj)
        data = super(ApiView, self).dispatch(request, *args, **kwargs)
        return HttpResponse(json.dumps(data), content_type='application/json')


class PollDeployment(ApiView):
    '''
    Clients regularly poll this view to retrieve deployment state.
    '''

    model = Deployment
    object_attr = 'deployment'

    def post(self, request, *args, **kwargs):
        node_name = request.POST['node_name']
        node, _ = Node.objects.get_or_create(deployment=self.deployment,
                name=node_name)
        data = model_to_dict(self.deployment.project)
        data.update(model_to_dict(self.deployment))
        del data['project']
        del data['owner']
        del data['id']
        data['commit'] = self.deployment.actual_commit()
        data['deployment_hash'] = self.deployment.hash()
        return data
