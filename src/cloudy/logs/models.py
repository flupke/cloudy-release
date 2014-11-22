from django.db import models
from django.contrib.auth.models import User


class LogEntry(models.Model):

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    text = models.TextField()
    user = models.ForeignKey(User, null=True, related_name='logs')
    link = models.CharField(max_length=255, null=True, db_index=True)
    project = models.ForeignKey('projects.Project', null=True,
            db_index=True, related_name='logs')
    deployment = models.ForeignKey('projects.Deployment', null=True,
            db_index=True, related_name='logs')

    def __unicode__(self):
        return self.text

    class Meta:
        ordering = ['-timestamp']
