from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView

from cloudy.crispy import crispy_context


admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='/projects/'), name='home'),
    url(r'^projects/', include('cloudy.projects.urls')),
    url(r'^api/', include('cloudy.api.urls')),
    url(r'^users/', include('cloudy.users.urls')),
    url(r'^logs/', include('cloudy.logs.urls')),

    url(r'^login/$', 'django.contrib.auth.views.login', {
            'template_name': 'users/login.html',
            'extra_context': crispy_context(),
        }, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {
            'template_name': 'users/logout.html',
        }, name='logout'),
    url(r'^admin/', include(admin.site.urls)),
)
