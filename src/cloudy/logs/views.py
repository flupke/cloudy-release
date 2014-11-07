from . import add_log


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
        resp = super(LogDeletionMixin, self).post(request, *args, **kwargs)
        object_name = self.get_logged_object_name()
        add_log(self.log_message, user=self.request.user,
                model_name=self.model.__name__.lower(),
                object_name=object_name)
        return resp
