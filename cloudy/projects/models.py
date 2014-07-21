import uuid
import hashlib
import collections
import json
import yaml

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property

from .exceptions import InvalidOperation, InternalError


DEPLOYMENT_VARIABLES_CHOICES = [
    ('yaml', 'YAML'),
    ('json', 'JSON'),
    ('python', 'Python'),
    ('shell', 'Shell'),
]
DEFAULT_DEPLOYMENT_VARIABLES_TYPE = 'yaml'


class Project(models.Model):
    '''
    Contains deployments' common data.
    '''

    name = models.CharField(_('project name'), max_length=255)
    key = models.CharField(_('key'), default=lambda: uuid.uuid4().hex,
            max_length=32, editable=False, db_index=True)

    repository_type = models.CharField(_('repository type'), max_length=255,
            choices=[('git', 'Git')], default='git')
    repository_url = models.CharField(_('repository URL'), max_length=2047)

    deployment_script_type = models.CharField(_('deployment script type'),
            max_length=32, choices=[
                ('bash', 'Bash script'),
                ('python_script', 'Python script'),
                ('python_entry_point', 'Python entry point '
                    '(path.to.module or path.to.module:function)'),
                ('python_file', 'Path to a python file'),
            ], default='bash')
    deployment_script = models.TextField(_('deployment script'),
            help_text='The script will be executed after the repository '
            'checkout, in the checkout directory.', blank=True)

    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('projects_update', [self.pk])

    class Meta:
        ordering = ['name']


class DeploymentBaseVariablesManager(models.Manager):

    def get_queryset(self):
        queryset = super(DeploymentBaseVariablesManager, self).get_queryset()
        return queryset.filter(deleted=False)


class DeploymentVariablesContainer(object):
    '''
    Mixin class holding common methods for models containing deployment
    variables.
    '''

    def vars_dict(self):
        '''
        Return the deployment variables as a dictionnary.
        '''
        if self.variables_format == 'json':
            ret = json.loads(self.variables)
        elif self.variables_format == 'yaml':
            ret = yaml.load(self.variables)
        elif self.variables_format == 'python':
            code = compile(self.variables, '<deployment variables>', 'exec')
            code_globals = {}
            exec(code, code_globals)
            code_globals.pop('__builtins__', None)
            ret = code_globals
        elif self.variables_format == 'shell':
            raise InvalidOperation('cannot convert shell deployment '
                    'variables to a dict')
        else:
            raise InternalError('unknwon variables format "%s"' %
                    self.variables_format)
        if not isinstance(ret, collections.Mapping):
            raise InvalidOperation('deployment variables are not a mapping')
        return ret

    def set_vars_from_dict(self, dct):
        '''
        Set the deployment variables to the encoded form of dict *dct*.
        '''
        if not isinstance(dct, collections.Mapping):
            raise InvalidOperation('deployment variables must be a mapping')
        if self.variables_format == 'json':
            self.variables = json.dumps(dct, indent=4)
        elif self.variables_format == 'yaml':
            self.variables = yaml.dump(dct)
        elif self.variables_format == 'python':
            lines = []
            for key, value in dct.items():
                lines.append('%s = %r' % (key, value))
            self.variables = '\n'.join(lines)
        elif self.variables_format == 'shell':
            raise InvalidOperation('cannot set shell deployment '
                    'from a dict')
        else:
            raise InternalError('unknwon variables format "%s"' %
                    self.variables_format)


class DeploymentBaseVariables(models.Model, DeploymentVariablesContainer):
    '''
    Can be used to define common deployment variables to be merged with
    variables in :class:`Deployment`.
    '''

    objects = DeploymentBaseVariablesManager()

    name = models.CharField(_('variables name'), max_length=255,
            db_index=True, unique=True)
    variables_format = models.CharField(_('deployment variables format'),
            max_length=32, choices=DEPLOYMENT_VARIABLES_CHOICES,
            default=DEFAULT_DEPLOYMENT_VARIABLES_TYPE)
    variables = models.TextField(_('deployment variables'), blank=True)

    deleted = models.BooleanField(editable=False, default=False, db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Deployment(models.Model, DeploymentVariablesContainer):
    '''
    Defines how a project is deployed on a specific set of nodes.
    '''

    project = models.ForeignKey(Project, related_name='deployments')
    name = models.CharField(_('deployment name'), max_length=255, db_index=True)
    key = models.CharField(_('key'), default=lambda: uuid.uuid4().hex,
            max_length=32, editable=False, db_index=True)

    base_dir = models.CharField(_('checkout base dir'), max_length=2047,
            help_text='The full path where the repository is checked out is '
            'base dir + project name. You can use "~" here.')

    commit = models.CharField(_('the commit to deploy'), max_length=255)

    base_variables = models.ForeignKey(DeploymentBaseVariables, null=True,
            blank=True)
    variables_format = models.CharField(_('deployment variables format'),
            max_length=32, choices=DEPLOYMENT_VARIABLES_CHOICES,
            default=DEFAULT_DEPLOYMENT_VARIABLES_TYPE)
    variables = models.TextField(_('deployment variables'), blank=True)
    redeploy_bit = models.CharField('used to manually force a redeploy',
            default=lambda: uuid.uuid4().hex, max_length=32, editable=False)

    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True)

    def source_url(self):
        '''
        Returns an URL representing what is deployed from the VCS.
        '''
        return '%s://%s@%s' % (self.project.repository_type,
                self.project.repository_url, self.commit)

    @models.permalink
    def get_absolute_url(self):
        return ('projects_deployment_overview', [self.pk])

    @cached_property
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
        hf.update(self.project.name)
        hf.update(self.project.repository_type)
        hf.update(self.project.repository_url)
        hf.update(self.project.deployment_script_type)
        hf.update(self.project.deployment_script)
        hf.update(self.base_dir)
        if self.base_variables is not None:
            hf.update(self.base_variables.variables_format)
            hf.update(self.base_variables.variables)
        hf.update(self.variables_format)
        hf.update(self.variables)
        hf.update(self.commit)
        hf.update(self.redeploy_bit)
        return hf.hexdigest()

    @cached_property
    def grouped_nodes(self):
        '''
        Returns this deployment's nodes grouped by similarities.
        '''
        groups = collections.defaultdict(list)
        for node in self.nodes.all():
            key = (node.last_deployment_status, node.last_deployed_source_url,
                    node.client_version)
            groups[key].append(node)
        return sorted(groups.values(), key=lambda g: -len(g))

    def trigger_redeploy(self):
        self.redeploy_bit = uuid.uuid4().hex
        self.save(update_fields=['redeploy_bit'])

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        unique_together = ['project', 'name']


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
    client_version = models.CharField('cloudy client version', max_length=32,
            null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True, db_index=True)

    def status_css_class(self):
        return self.STATUS_CSS_CLASSES[self.last_deployment_status]

    def last_deployment_output_is_relevant(self):
        return self.last_deployment_status in ('success', 'error')

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ('deployment', 'name')


class DeploymentLogEntry(models.Model):
    '''
    Stores a log entry for a deployment.
    '''

    node = models.ForeignKey(Node)
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    source_url = models.TextField(_('deployment source'),
            help_text='the combined repository type, URL and commit')
    type = models.CharField(max_length=255)
    text = models.TextField(null=True)

    class Meta:
        ordering = ['-date']
