from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from annoying.fields import AutoOneToOneField

from cloudy.utils import uuid_hex


class UserProfile(models.Model):

    user = AutoOneToOneField(User, related_name='profile')
    secret = models.CharField(max_length=32, default=uuid_hex, db_index=True)

    def get_absolute_url(self):
        return reverse('users_profile', kwargs={'pk': self.pk})
