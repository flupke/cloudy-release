from django.conf.urls import patterns, include, url
from django.contrib import admin

from cloudy.users.forms import LoginForm


admin.autodiscover()


urlpatterns = patterns('',
    url(r'^', include('cloudy.projects.urls')),
    url(r'^login/$', 'django.contrib.auth.views.login', {
            'authentication_form': LoginForm,
            'template_name': 'users/login.html',
        }, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {
            'template_name': 'users/logout.html',
        }, name='logout'),
    url(r'^admin/', include(admin.site.urls)),
)
