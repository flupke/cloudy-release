import uuid

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class Project(models.Model):
    '''
    Contains deployments' common data.
    '''

    name = models.CharField(_('project name'), max_length=255)
    key = models.CharField(_('key'), default=lambda: uuid.uuid4().hex,
            max_length=32, editable=False, db_index=True)

    repository_type = models.CharField(_('repository type'), max_length=255,
            choices=[('git', 'Git')], default='git')
    repository_url = models.TextField(_('repository URL'))

    commit = models.CharField(_('the commit to deploy'), max_length=255,
            blank=True)

    deploy_script_type = models.CharField(_('deploy script type'),
            max_length=32, choices=[
                ('bash', 'Bash'),
                ('python_script', 'Python script'),
                ('python_entry_point', 'Python entry point'),
            ], default='bash')
    deploy_script = models.TextField(_('deploy script'), 
            help_text='The script will be executed after the repository '
            'checkout, in the checkout directory.', blank=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('projects_update', [self.pk])


class Deployment(models.Model):
    '''
    Defines how a project is deployed on a specific set of nodes.
    '''

    project = models.ForeignKey(Project)
    name = models.CharField(_('deployment'), max_length=255)
    key = models.CharField(_('key'), default=lambda: uuid.uuid4().hex,
            max_length=32, editable=False, db_index=True)

    base_dir = models.TextField(_('the base directory where the code '
            'is checked out'))    

    variables_format = models.CharField(_('deployment variables format'),
            max_length=32, choices=[
                ('yaml', 'YAML'),
                ('json', 'JSON'),
                ('python', 'Python'),
            ])
    variables = models.TextField(_('deployment variables'), blank=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)


class Node(models.Model):
    '''
    Stores deployment status of a single node.
    '''

    deployment = models.ForeignKey(Deployment)
    name = models.CharField(_('node name'), max_length=255)

    last_deployment_status = models.CharField(_('last deployment status'),
            max_length=16, null=True, choices=[
                ('pending', 'Pending'),
                ('success', 'Success'),
                ('error', 'Error'),
            ])
    last_deployment_output = models.TextField(_('last deployment output'),
            null=True)
    last_deployed_source_url = models.TextField(_('last deployed commit'),
            null=True, help_text='The last commit that was deployed, '
            'successfully or not.')
    last_deployment_date = models.DateTimeField(_('last deployment date'),
            null=True)

    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('deployment', 'name')


class DeploymentLogEntry(models.Model):
    '''
    Stores a log entry for a deployment.
    '''

    deployment = models.ForeignKey(Deployment)
    node = models.ForeignKey(Node)
    date = models.DateTimeField(auto_now_add=True)
    source_url = models.TextField(_('deployment source'), 
            help_text='the combined repository type, URL and commit')
    type = models.CharField(max_length=255)
    text = models.TextField(null=True)
