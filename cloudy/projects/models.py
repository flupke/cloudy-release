import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Project(models.Model):

    name = models.CharField(_('project'), max_length=255)
    key = models.CharField(_('key'), default=lambda: uuid.uuid4().hex,
            max_length=32, editable=False)
