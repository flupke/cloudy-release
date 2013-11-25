from django.conf.urls import patterns, url

from .views import ProjectsList


urlpatterns = patterns('',
    url(r'^$', ProjectsList.as_view()),
)
