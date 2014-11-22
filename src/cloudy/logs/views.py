from django.core.urlresolvers import reverse
from vanilla import ListView

from cloudy.views import CloudyViewMixin
from cloudy.projects.models import Project, Deployment
from . import add_log, get_object_link
from .models import LogEntry


class LoggingMixinBase(object):

    def get_logged_object_name(self):
        return unicode(self.object)


class LogCreationMixin(LoggingMixinBase):
    '''
    Mixin class to be used with :class:`vanilla.CreateView`, logging a message
    on success.
    '''

    log_message = '{user} created {model_name} {object_name}'

    def form_valid(self, form):
        resp = super(LogCreationMixin, self).form_valid(form)
        object_name = self.get_logged_object_name()
        add_log(self.log_message, user=self.request.user,
                model_name=self.model.__name__.lower(),
                object_name=object_name, object=self.object)
        return resp


class LogUpdateMixin(LoggingMixinBase):
    '''
    Mixin class to be used with :class:`vanilla.UpdateView`, logging a message
    on success.
    '''

    log_message = '{user} edited {model_name} {object_name}'

    def form_valid(self, form):
        object_name = self.get_logged_object_name()
        add_log(self.log_message, user=self.request.user,
                object_name=object_name,
                model_name=self.model.__name__.lower(), object=self.object)
        return super(LogUpdateMixin, self).form_valid(form)


class LogDeletionMixin(LoggingMixinBase):
    '''
    Mixin class to be used with :class:`vanilla.CreateView`, logging a message
    on confirmation.
    '''

    log_message = '{user} deleted {model_name} {object_name}'

    def post(self, request, *args, **kwargs):
        # Remove dead links
        self.object = self.get_object()
        link = get_object_link(self.object)
        if link is not None:
            LogEntry.objects.filter(link=link).update(link=None)

        object_name = self.get_logged_object_name()
        add_log(self.log_message, user=self.request.user,
                model_name=self.model.__name__.lower(),
                object_name=object_name)

        return super(LogDeletionMixin, self).post(request, *args, **kwargs)


class LogEntriesList(CloudyViewMixin, ListView):

    model = LogEntry
    paginate_by = 50
    context_object_name = 'logs'
    filter_obj_name = None

    @property
    def breadcrumbs(self):
        if self.filter_obj_name is None:
            return [('Logs', None)]
        elif self.filter_obj_name == 'project':
            return [
                ('Logs', reverse('logs_list')),
                (self.filter_obj, None),
            ]
        elif self.filter_obj_name == 'deployment':
            project = self.filter_obj.project
            return [
                ('Logs', reverse('logs_list')),
                (self.filter_obj.project, reverse('projects_logs',
                    kwargs={'project_id': project.pk})),
                (self.filter_obj, None),
            ]

    @property
    def heading(self):
        if self.filter_obj_name is None:
            return 'Logs'
        elif self.filter_obj_name == 'project':
            return 'Logs for project %s' % self.filter_obj
        elif self.filter_obj_name == 'deployment':
            return 'Logs for deployment %s' % self.filter_obj

    def get_queryset(self):
        qs = super(LogEntriesList, self).get_queryset()
        if self.filter_obj_name is not None:
            kwargs = {self.filter_obj_name: self.filter_obj}
            qs = qs.filter(**kwargs)
        return qs

    def dispatch(self, request, *args, **kwargs):
        if self.filter_obj_name == 'project':
            self.filter_obj = Project.objects.get(pk=kwargs['project_id'])
        elif self.filter_obj_name == 'deployment':
            self.filter_obj = Deployment.objects.get(pk=kwargs['deployment_id'])
        elif self.filter_obj_name is not None:
            raise ValueError('invalid value for filter_obj_name: %s' %
                    self.filter_obj_name)
        return super(LogEntriesList, self).dispatch(request, *args, **kwargs)
