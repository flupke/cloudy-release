from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import ProjectsList, CreateProject


urlpatterns = patterns('',
    url(r'^$', login_required(ProjectsList.as_view()), name='projects_list'),
    url(r'^projects/create/$', login_required(CreateProject.as_view()),
        name='projects_create'),
)
