from vanilla import ListView, CreateView, UpdateView
from crispy_forms.layout import Field, Layout

from cloudy.crispy import crispy_context
from .models import Project


class ProjectsList(ListView):

    model = Project


class EditProjectMixin(object):

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
        context = super(EditProjectMixin, self).get_context_data(**context)
        context.update(crispy_context(layout=self.crispy_layout()))
        return context

    def get_form(self, data=None, files=None, **kwargs):
        '''
        Returns a form instance.
        '''
        return super(EditProjectMixin, self).get_form(data=data, files=files,
                initial={'owner': self.request.user}, **kwargs)


class CreateProject(EditProjectMixin, CreateView):

    pass


class UpdateProject(EditProjectMixin, UpdateView):

    pass
