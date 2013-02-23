from django.conf.urls import patterns, include, url
from django.contrib import admin

from cloudy.views import DashboardView


admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', DashboardView.as_view(), name='dashboard'),

    url(r'^admin/', include(admin.site.urls)),
)
