from vanilla import ListView, CreateView, UpdateView, DeleteView, DetailView
from crispy_forms.layout import Field, Layout
from django.views.generic import View
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.forms import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect

from cloudy.crispy import crispy_context
from cloudy.logs import add_log
from .models import (Project, Deployment, DeploymentLogEntry, Node,
        DeploymentBaseVariables)
from .forms import EditDeploymentForm, EditDeploymentBaseVariablesForm


class ProjectsMixin(object):
    '''
    Mixin class for all views in this app.
    '''

    heading = None
    breadcrumbs = []

    def get_context_data(self, **context):
        path = self.request.path
        if path.startswith('/projects/base-variables/'):
            menu_item = 'base_variables'
        else:
            menu_item = 'projects'
        return super(ProjectsMixin, self).get_context_data(
                heading=self.heading, breadcrumbs=self.breadcrumbs,
                menu_item=menu_item, **context)

# ----------------------------------------------------------------------------
# Projects views

class ProjectsList(ProjectsMixin, ListView):

    model = Project
    heading = 'Projects'
    breadcrumbs = [
        ('Projects', None)
    ]


class EditProjectMixin(ProjectsMixin):

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


class CreateProject(EditProjectMixin, CreateView):

    heading = 'Create project'
    breadcrumbs = [
        ('Projects', reverse_lazy('projects_list')),
        ('Create project', None),
    ]


class UpdateProject(EditProjectMixin, UpdateView):

    heading = 'Configure project'
    breadcrumbs = [
        ('Projects', reverse_lazy('projects_list')),
        ('Configure project', None),
    ]

    def form_valid(self, form):
        add_log('{user} edited project "{object}"', object=self.object,
                user=self.request.user)
        return super(UpdateProject, self).form_valid(form)


class DeleteProject(ProjectsMixin, DeleteView):

    model = Project
    heading = 'Delete project'
    breadcrumbs = [
        ('Projects', reverse_lazy('projects_list')),
        ('Delete project', None),
    ]

    def get_success_url(self):
        return reverse('projects_list')

# ----------------------------------------------------------------------------
# Deployment views

class DeploymentViewsMixin(ProjectsMixin):

    @property
    def project(self):
        return self.object.project

    @property
    def breadcrumbs(self):
        return [
            ('Projects', reverse_lazy('projects_list')),
            (self.project, self.project.get_absolute_url()),
            (self.heading, None),
        ]


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

    @property
    def breadcrumbs(self):
        return [
            ('Projects', reverse_lazy('projects_list')),
            (self.project, self.project.get_absolute_url()),
            (self.heading, None),
        ]

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


class CreateDeployment(EditDeploymentMixin, CreateView):

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


class UpdateDeployment(EditDeploymentMixin, UpdateView):

    heading = 'Configure deployment'


class DeleteDeployment(DeploymentViewsMixin, DeleteView):

    model = Deployment
    heading = 'Delete deployment'

    def get_success_url(self):
        return reverse('projects_list')


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

class NodeViewsMixin(ProjectsMixin):

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

class BaseVariablesList(ProjectsMixin, ListView):

    model = DeploymentBaseVariables
    context_object_name = 'base_variables_list'
    heading = 'Base variables'
    breadcrumbs = [(heading, None)]


class EditBaseVariablesMixin(ProjectsMixin):

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
    breadcrumbs = [
        ('Base variables', reverse_lazy('projects_base_variables_list')),
        (heading, None),
    ]


class DeleteBaseVariables(ProjectsMixin, DeleteView):

    model = DeploymentBaseVariables
    success_url = reverse_lazy('projects_base_variables_list')
    heading = 'Delete base variables'
    breadcrumbs = [
        ('Base variables', reverse_lazy('projects_base_variables_list')),
        (heading, None),
    ]

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.deleted = True
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

