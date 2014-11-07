class CloudyViewMixin(object):
    '''
    Mixin class for all views in this app.
    '''

    heading = None
    breadcrumbs = []
    menu_item = None

    def get_context_data(self, **context):
        return super(CloudyViewMixin, self).get_context_data(
                heading=self.heading, breadcrumbs=self.breadcrumbs,
                menu_item=self.menu_item, **context)
