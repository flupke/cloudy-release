from vanilla import ListView, CreateView, UpdateView, DeleteView, DetailView
from crispy_forms.layout import Field, Layout
from django.views.generic import View
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.forms import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect

from cloudy.crispy import crispy_context
from cloudy.logs.models import LogEntry
from cloudy.logs.views import (LogUpdateMixin, LogCreationMixin,
        LogDeletionMixin)
from cloudy.views import CloudyViewMixin
from .models import (Project, Deployment, DeploymentLogEntry, Node,
        DeploymentBaseVariables)
from .forms import EditDeploymentForm, EditDeploymentBaseVariablesForm


# ----------------------------------------------------------------------------
# Projects views

class ProjectsList(CloudyViewMixin, ListView):

    model = Project
    heading = 'Projects'
    breadcrumbs = [
        ('Projects', None)
    ]
    menu_item = 'projects'

    def get_context_data(self, **kwargs):
        logs = LogEntry.objects.all()[:50]
        return super(ProjectsList, self).get_context_data(logs=logs, **kwargs)


class ProjectMixin(CloudyViewMixin):

    @property
    def breadcrumbs(self):
        tail = getattr(self, 'object', self.heading)
        return [
            ('Projects', reverse_lazy('projects_list')),
            (tail, None),
        ]


class EditProjectMixin(ProjectMixin):

    model = Project

    def crispy_layout(self):
        '''
        Create a custom crispy layout with the "owner" field rendered as a
        hidden field.
        '''
        form = self.get_form()
        fields = []
        for field in form.fields.keys():
            if field == 'owner':
                field = Field(field, type='hidden')
            fields.append(field)
        return Layout(*fields)

    def get_context_data(self, **context):
        layout = self.crispy_layout()
        context.update(crispy_context(layout=layout, html5=False))
        return super(EditProjectMixin, self).get_context_data(
                **context)

    def get_form(self, data=None, files=None, **kwargs):
        return super(EditProjectMixin, self).get_form(data=data, files=files,
                initial={'owner': self.request.user}, **kwargs)

    def get_success_url(self):
        return reverse('projects_list')


class CreateProject(EditProjectMixin, LogCreationMixin, CreateView):

    heading = 'Create project'


class UpdateProject(EditProjectMixin, LogUpdateMixin, UpdateView):

    heading = 'Configure project'


class DeleteProject(ProjectMixin, LogDeletionMixin, DeleteView):

    model = Project
    heading = 'Delete project'
    success_url = reverse_lazy('projects_list')

# ----------------------------------------------------------------------------
# Deployment views

class DeploymentViewsMixin(CloudyViewMixin):

    @property
    def project(self):
        return self.object.project

    @property
    def breadcrumbs(self):
        tail = getattr(self, 'object', self.heading)
        return [
            ('Projects', reverse_lazy('projects_list')),
            (self.project, self.project.get_absolute_url()),
            (tail, None),
        ]

    def get_logged_object_name(self):
        return u'%s/%s' % (self.object.project, self.object)


class EditDeploymentMixin(DeploymentViewsMixin):

    model = Deployment
    form_class = EditDeploymentForm

    @property
    def project(self):
        if not hasattr(self, '_project'):
            project_pk = self.request.resolver_match.kwargs.get('project_pk')
            if project_pk is not None:
                self._project = get_object_or_404(Project,
                        pk=project_pk)
            else:
                self._project = self.object.project
        return self._project

    def crispy_layout(self):
        '''
        Create a custom crispy layout with the "project" field rendered as a
        hidden field.
        '''
        form = self.get_form()
        fields = []
        for field in form.fields.keys():
            if field == 'project':
                field = Field(field, type='hidden')
            fields.append(field)
        return Layout(*fields)

    def get_context_data(self, **context):
        layout = self.crispy_layout()
        context.update(crispy_context(layout=layout, html5_required=False))
        return super(EditDeploymentMixin, self).get_context_data(
                **context)

    def get_form(self, data=None, files=None, **kwargs):
        initial = kwargs.get('initial', {})
        initial['project'] = self.project
        kwargs['initial'] = initial
        return super(EditDeploymentMixin, self).get_form(data=data, files=files,
                **kwargs)

    def get_success_url(self):
        return reverse('projects_deployment_overview',
                kwargs={'pk': self.object.pk})


class CreateDeployment(EditDeploymentMixin, LogCreationMixin, CreateView):

    heading = 'Create deployment'

    def get_form(self, data=None, files=None, **kwargs):
        copy_from = self.request.GET.get('copy_from')
        if copy_from is not None:
            deployment = Deployment.objects.get(pk=copy_from)
            initial = model_to_dict(deployment)
            del initial['id']
        else:
            initial = {}
        kwargs['initial'] = initial
        return super(CreateDeployment, self).get_form(data=data, files=files,
                **kwargs)


class UpdateDeployment(EditDeploymentMixin, LogUpdateMixin, UpdateView):

    heading = 'Configure deployment'


class DeleteDeployment(DeploymentViewsMixin, LogDeletionMixin, DeleteView):

    model = Deployment
    heading = 'Delete deployment'
    success_url = reverse_lazy('projects_list')


class DeploymentOverview(DeploymentViewsMixin, DetailView):

    model = Deployment
    template_name = 'projects/deployment_overview.html'
    object_name = 'deployment'

    @property
    def heading(self):
        return self.object

    def get_context_data(self, **context):
        poll_url = self.request.build_absolute_uri(
                reverse('api_poll_deployment', kwargs={'key': self.object.key}))
        context['poll_url'] = poll_url
        return super(DeploymentOverview, self).get_context_data(**context)

# ----------------------------------------------------------------------------
# Nodes

class NodeViewsMixin(CloudyViewMixin):

    @property
    def node(self):
        if not hasattr(self, '_node'):
            pk = self.request.resolver_match.kwargs['pk']
            self._node = get_object_or_404(Node, pk=pk)
        return self._node

    @property
    def breadcrumbs(self):
        project = self.node.deployment.project
        deployment = self.node.deployment
        return [
            ('Projects', reverse_lazy('projects_list')),
            (project, project.get_absolute_url()),
            (deployment, deployment.get_absolute_url()),
            (self.heading, None)
        ]


class NodeLogs(NodeViewsMixin, ListView):

    model = DeploymentLogEntry
    context_object_name = 'entries'

    @property
    def heading(self):
        return u'%s logs' % self.node

    def get_queryset(self):
        qs = super(NodeLogs, self).get_queryset()
        return qs.filter(node=self.node)


class DeleteNode(View):

    def post(self, request):
        pk = request.POST['pk']
        node = get_object_or_404(Node, pk=pk)
        node.delete()
        return HttpResponse()

# ----------------------------------------------------------------------------
# Base variables

class BaseVariablesList(CloudyViewMixin, ListView):

    model = DeploymentBaseVariables
    context_object_name = 'base_variables_list'
    heading = 'Base variables'
    breadcrumbs = [(heading, None)]
    menu_item = 'base_variables'


class EditBaseVariablesMixin(CloudyViewMixin):

    model = DeploymentBaseVariables
    form_class = EditDeploymentBaseVariablesForm
    success_url = reverse_lazy('projects_base_variables_list')

    def get_context_data(self, **context):
        context.update(crispy_context(html5_required=False))
        return super(EditBaseVariablesMixin, self).get_context_data(
                **context)


class CreateBaseVariables(EditBaseVariablesMixin, CreateView):

    heading = 'Create base variables'
    breadcrumbs = [
        ('Base variables', reverse_lazy('projects_base_variables_list')),
        (heading, None),
    ]

    def get_form(self, data=None, files=None, **kwargs):
        copy_from = self.request.GET.get('copy_from')
        if copy_from is not None:
            base_variables = DeploymentBaseVariables.objects.get(pk=copy_from)
            initial = model_to_dict(base_variables)
            del initial['id']
        else:
            initial = {}
        kwargs['initial'] = initial
        return super(CreateBaseVariables, self).get_form(data=data, files=files,
                **kwargs)

class UpdateBaseVariables(EditBaseVariablesMixin, UpdateView):

    heading = 'Edit base variables'

    @property
    def breadcrumbs(self):
        return [
            ('Base variables', reverse_lazy('projects_base_variables_list')),
            (self.object, None),
        ]


class DeleteBaseVariables(CloudyViewMixin, DeleteView):

    model = DeploymentBaseVariables
    success_url = reverse_lazy('projects_base_variables_list')
    heading = 'Delete base variables'

    @property
    def breadcrumbs(self):
        return [
            ('Base variables', reverse('projects_base_variables_list')),
            (self.object, None),
        ]

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.deleted = True
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
