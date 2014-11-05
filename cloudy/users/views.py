from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from vanilla import UpdateView

from cloudy.utils import uuid_hex
from .models import UserProfile
from .forms import UserProfileForm


class UpdateUserProfile(UpdateView):

    model = UserProfile
    form_class = UserProfileForm

    def get_context_data(self, **kwargs):
        if self.request.user == self.object.user:
            menu_item = 'users_profile'
        else:
            menu_item = None
        return super(UpdateUserProfile, self).get_context_data(
                menu_item=menu_item, **kwargs)

    def get_success_url(self):
        return reverse('users_profile', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if 'gen_auth_key' in self.request.POST:
            self.object.auth_key = uuid_hex()
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
