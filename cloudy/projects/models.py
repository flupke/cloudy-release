import uuid
import hashlib
import collections

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
            blank=True, help_text='Deployments commits will override this '
            'value.' )

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

    class Meta:
        ordering = ['-date_created']


class Deployment(models.Model):
    '''
    Defines how a project is deployed on a specific set of nodes.
    '''

    project = models.ForeignKey(Project, related_name='deployments')
    name = models.CharField(_('deployment name'), max_length=255)
    key = models.CharField(_('key'), default=lambda: uuid.uuid4().hex,
            max_length=32, editable=False, db_index=True)

    base_dir = models.TextField(_('checkout base dir'), 
            help_text='The full path where the repository is checked out is '
            'base dir + project name.')

    commit = models.CharField(_('the commit to deploy'), max_length=255,
            blank=True, help_text='Leave blank to use the project\'s global '
            'commit.')

    variables_format = models.CharField(_('deployment variables format'),
            max_length=32, choices=[
                ('yaml', 'YAML'),
                ('json', 'JSON'),
                ('python', 'Python'),
            ], default='yaml')
    variables = models.TextField(_('deployment variables'), blank=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def actual_commit(self):
        '''
        Returns the commit to deploy, either this deployment's commit, or the
        project's commit.
        '''
        if self.commit:
            return self.commit
        return self.project.commit
    
    def source_url(self):
        '''
        Returns an URL representing what is deployed from the VCS.
        '''
        return '%s://%s@%s' % (self.project.repository_type,
                self.project.repository_url, self.actual_commit())

    @models.permalink
    def get_absolute_url(self):
        return ('projects_deployment_overview', [self.pk])

    def nodes_info(self):
        '''
        Returns a list of tuples condaining summarized nodes informations.
        
        The tuples contain ``(status_label, count, css_class)`` for each
        status.
        '''
        counters = collections.defaultdict(int)
        css_classes = {} 
        for node in self.nodes.all():
            label = node.get_last_deployment_status_display()
            css_classes[label] = node.status_css_class()
            counters[label] += 1
        ret = []
        for _, label in Node.STATUS_CHOICES:
            if label in counters:
                ret.append((label, counters[label], css_classes[label]))
        return ret

    def hash(self):
        '''
        Returns a string that uniquely identifies the characteristics of this
        deployment.
        '''
        hf = hashlib.sha1()
        hf.update(self.project.repository_type)
        hf.update(self.project.repository_url)
        hf.update(self.project.deploy_script_type)
        hf.update(self.project.deploy_script)
        hf.update(self.base_dir)
        hf.update(self.variables_format)
        hf.update(self.variables)
        hf.update(self.actual_commit())
        return hf.hexdigest()

    def overview_heading(self):
        return u'"%s" deployment overview' % self

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['-date_created']


class Node(models.Model):
    '''
    Stores deployment status of a single node.
    '''

    STATUS_CSS_CLASSES = {
        'unknown': 'label-default',
        'pending': 'label-info',
        'success': 'label-success',
        'error': 'label-danger',
    }
    STATUS_CHOICES = [
        ('unknown', 'Unknown'),
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('error', 'Error'),
    ]

    deployment = models.ForeignKey(Deployment, related_name='nodes')
    name = models.CharField(_('node name'), max_length=255)

    last_deployment_status = models.CharField(_('last deployment status'),
            max_length=16, choices=STATUS_CHOICES, default='unknown')
    last_deployment_output = models.TextField(_('last deployment output'),
            null=True)
    last_deployed_source_url = models.TextField(_('last deployed commit'),
            null=True, help_text='The last commit that was deployed, '
            'successfully or not.')
    last_deployment_date = models.DateTimeField(_('last deployment date'),
            null=True)

    date_created = models.DateTimeField(auto_now_add=True)

    def status_css_class(self):
        return self.STATUS_CSS_CLASSES[self.last_deployment_status]

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ('deployment', 'name')


class DeploymentLogEntry(models.Model):
    '''
    Stores a log entry for a deployment.
    '''

    node = models.ForeignKey(Node)
    date = models.DateTimeField(auto_now_add=True)
    source_url = models.TextField(_('deployment source'), 
            help_text='the combined repository type, URL and commit')
    type = models.CharField(max_length=255)
    text = models.TextField(null=True)
