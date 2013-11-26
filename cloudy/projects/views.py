from vanilla import ListView, CreateView, UpdateView, DeleteView
from crispy_forms.layout import Field, Layout

from cloudy.crispy import crispy_context
from .models import Project


class ProjectsMixin(object):

    heading = None

    def get_context_data(self, **context):
        return super(ProjectsMixin, self).get_context_data(
                heading=self.heading, **context)


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
        '''
        Returns a form instance.
        '''
        return super(EditProjectMixin, self).get_form(data=data, files=files,
                initial={'owner': self.request.user}, **kwargs)


class CreateProject(EditProjectMixin, CreateView):

    heading = 'Create project'


class UpdateProject(EditProjectMixin, UpdateView):

    heading = 'Update project'


class DeleteProject(ProjectsMixin, DeleteView):

    model = Project
    heading = 'Delete project'
    success_url = '/'
