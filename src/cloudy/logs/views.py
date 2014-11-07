from vanilla import ListView

from cloudy.views import CloudyViewMixin
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

    heading = 'Logs'
    breadcrumbs = [('Logs', None)]
    model = LogEntry
    paginate_by = 50
    context_object_name = 'logs'
