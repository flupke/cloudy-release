from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import (ProjectsList, CreateProject, UpdateProject, DeleteProject,
        CreateDeployment, UpdateDeployment, DeploymentOverview,
        DeleteDeployment)


urlpatterns = patterns('',
    # Projects
    url(r'^$', login_required(ProjectsList.as_view()), name='projects_list'),
    url(r'^create/$', login_required(CreateProject.as_view()),
        name='projects_create'),
    url(r'^(?P<pk>\d+)/$', login_required(UpdateProject.as_view()),
        name='projects_update'),
    url(r'^(?P<pk>\d+)/delete/$', 
        login_required(DeleteProject.as_view()), name='projects_delete'),

    # Deployments
    url(r'^(?P<project_pk>\d+)/deployments/create/$',
        login_required(CreateDeployment.as_view()),
        name='projects_create_deployment'),
    url(r'^deployments/(?P<pk>\d+)/$',
        login_required(UpdateDeployment.as_view()),
        name='projects_update_deployment'),
    url(r'^deployments/(?P<pk>\d+)/delete/$',
        login_required(DeleteDeployment.as_view()),
        name='projects_delete_deployment'),
    url(r'^deployments/(?P<pk>\d+)/overview/$',
        login_required(DeploymentOverview.as_view()),
        name='projects_deployment_overview'),
)
