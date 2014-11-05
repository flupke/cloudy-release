from django.db import models
from django.contrib.auth.models import User
from annoying.fields import AutoOneToOneField

from cloudy.utils import uuid_hex


class UserProfile(models.Model):

    user = AutoOneToOneField(User, related_name='profile')
    auth_key = models.CharField(max_length=32, default=uuid_hex)
