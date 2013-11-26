from vanilla import ListView, CreateView, UpdateView, DeleteView, DetailView
from crispy_forms.layout import Field, Layout
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404

from cloudy.crispy import crispy_context
from .models import Project, Deployment


class ProjectsMixin(object):
    '''
    Mixin class for all views in this app.
    '''

    heading = None
    breadcrumbs = []

    def get_context_data(self, **context):
        return super(ProjectsMixin, self).get_context_data(
                heading=self.heading, breadcrumbs=self.breadcrumbs, **context)

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
        context.update(crispy_context(layout=layout))
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

    @property
    def project(self):
        if not hasattr(self, '_project'):
            if self.project_pk is not None:
                self._project = get_object_or_404(Project,
                        pk=self.project_pk)
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

    def dispatch(self, request, project_pk=None, **kwargs):
        self.project_pk = project_pk
        return super(EditDeploymentMixin, self).dispatch(request,
                project_pk=project_pk, **kwargs)

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
        context.update(crispy_context(layout=layout))
        return super(EditDeploymentMixin, self).get_context_data(
                **context)

    def get_form(self, data=None, files=None, **kwargs):
        return super(EditDeploymentMixin, self).get_form(data=data, files=files,
                initial={'project': self.project}, **kwargs)

    def get_success_url(self):
        return reverse('projects_list')


class CreateDeployment(EditDeploymentMixin, CreateView):

    heading = 'Create deployment'


class UpdateDeployment(EditDeploymentMixin, UpdateView):

    heading = 'Configure deployment'

    def get_success_url(self):
        return reverse('projects_deployment_overview', 
                kwargs={'pk': self.object.pk})

        
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
        return u'"%s" deployment overview' % self.object

    def get_context_data(self, **context):
        poll_url = self.request.build_absolute_uri(
                reverse('api_poll_deployment', kwargs={'key': self.object.key}))
        context['poll_url'] = poll_url
        return super(DeploymentOverview, self).get_context_data(**context)
    
