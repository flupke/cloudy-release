from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import UsersList, UpdateUserProfile, CreateUser


urlpatterns = patterns('',
    url(r'^$', login_required(UsersList.as_view()), name='users_list'),
    url(r'^create/$', login_required(CreateUser.as_view()),
        name='users_create'),
    url(r'^(?P<pk>\d+)/$', login_required(UpdateUserProfile.as_view()),
        name='users_profile'),
)
