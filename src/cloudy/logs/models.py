from django.db import models
from django.contrib.auth.models import User


class LogEntry(models.Model):

    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    user = models.ForeignKey(User, null=True, related_name='logs')
    link = models.CharField(max_length=255, null=True)

    def __unicode__(self):
        return self.text
