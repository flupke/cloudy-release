from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import UsersList, UpdateUserProfile


urlpatterns = patterns('',
    url(r'^$', login_required(UsersList.as_view()), name='users_list'),
    url(r'^(?P<pk>\d+)/$', login_required(UpdateUserProfile.as_view()),
        name='users_profile'),
)
