from vanilla import ListView, CreateView, UpdateView, DeleteView, DetailView
from crispy_forms.layout import Field, Layout
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from cloudy.crispy import crispy_context
from .models import Project, Deployment


class ProjectsMixin(object):
    '''
    Mixin class for all views in this app.
    '''

    heading = None

    def get_context_data(self, **context):
        return super(ProjectsMixin, self).get_context_data(
                heading=self.heading, **context)

# ----------------------------------------------------------------------------
# Projects views

class ProjectsList(ProjectsMixin, ListView):

    model = Project
    heading = 'Projects'


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


class UpdateProject(EditProjectMixin, UpdateView):

    heading = 'Configure project'


class DeleteProject(ProjectsMixin, DeleteView):

    model = Project
    heading = 'Delete project'

    def get_success_url(self):
        return reverse('projects_list')

# ----------------------------------------------------------------------------
# Deployment views

class EditDeploymentMixin(ProjectsMixin):

    model = Deployment

    def dispatch(self, request, project_pk=None, **kwargs):
        if project_pk is not None:
            self.project_object = get_object_or_404(Project, pk=project_pk)
        else:
            self.project_object = None
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
        if self.project_object is not None:
            initial = {'project': self.project_object}
        else:
            initial = {'project': self.object.project}
        return super(EditDeploymentMixin, self).get_form(data=data, files=files,
                initial=initial, **kwargs)

    def get_success_url(self):
        return reverse('projects_list')


class CreateDeployment(EditDeploymentMixin, CreateView):

    heading = 'Create deployment'


class UpdateDeployment(EditDeploymentMixin, UpdateView):

    heading = 'Configure deployment'

    def get_success_url(self):
        return reverse('projects_deployment_overview', 
                kwargs={'pk': self.object.pk})


class DeploymentOverview(ProjectsMixin, DetailView):

    model = Deployment
    template_name = 'projects/deployment_overview.html'
    object_name = 'deployment'
    
