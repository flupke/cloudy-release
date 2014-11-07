from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import LogEntriesList


urlpatterns = patterns('',
    url(r'^$', login_required(LogEntriesList.as_view()), name='logs_list'),
)
