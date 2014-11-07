from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from vanilla import UpdateView, ListView, CreateView

from cloudy.utils import uuid_hex
from cloudy.views import CloudyViewMixin
from .models import UserProfile
from .forms import UserProfileForm, UserCreationFormWithEmail


class UsersList(CloudyViewMixin, ListView):

    heading = 'Users'
    breadcrumbs = [('Users', None)]
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    menu_item = 'users'


class UpdateUserProfile(CloudyViewMixin, UpdateView):

    heading = 'Profile'
    model = UserProfile
    form_class = UserProfileForm

    @property
    def breadcrumbs(self):
        return [
            ('Users', reverse_lazy('users_list')),
            (self.object.user, None),
        ]

    @property
    def menu_item(self):
        if self.request.user.pk == self.object.pk:
            return 'users_profile'

    def get_success_url(self):
        return reverse('users_profile', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if 'gen_secret' in self.request.POST:
            self.object.secret = uuid_hex()
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class CreateUser(CloudyViewMixin, CreateView):

    heading = 'Create user'
    breadcrumbs = [
        ('Users', reverse_lazy('users_list')),
        ('Create pser', None),
    ]

    model = User
    template_name = 'users/user_form.html'
    form_class = UserCreationFormWithEmail
    success_url = reverse_lazy('users_list')
