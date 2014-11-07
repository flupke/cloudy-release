from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from vanilla import UpdateView

from cloudy.utils import uuid_hex
from cloudy.views import CloudyViewMixin
from .models import UserProfile
from .forms import UserProfileForm


class UpdateUserProfile(CloudyViewMixin, UpdateView):

    heading = 'Profile'
    breadcrumbs = [('Profile', None)]
    model = UserProfile
    form_class = UserProfileForm
    menu_item = 'users_profile'

    def get_success_url(self):
        return reverse('users_profile', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if 'gen_secret' in self.request.POST:
            self.object.secret = uuid_hex()
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
