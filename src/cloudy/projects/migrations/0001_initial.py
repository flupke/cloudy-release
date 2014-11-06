# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cloudy.projects.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Deployment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='deployment name', db_index=True)),
                ('key', models.CharField(default=cloudy.projects.models.uuid_hex, verbose_name='key', max_length=32, editable=False, db_index=True)),
                ('base_dir', models.CharField(help_text=b'The full path where the repository is checked out is base dir + project name. You can use "~" here.', max_length=2047, verbose_name='checkout base dir')),
                ('commit', models.CharField(max_length=255, verbose_name='the commit to deploy')),
                ('variables_format', models.CharField(default=b'yaml', max_length=32, verbose_name='deployment variables format', choices=[(b'yaml', b'YAML'), (b'json', b'JSON'), (b'python', b'Python'), (b'shell', b'Shell')])),
                ('variables', models.TextField(verbose_name='deployment variables', blank=True)),
                ('redeploy_bit', models.CharField(default=cloudy.projects.models.uuid_hex, verbose_name=b'used to manually force a redeploy', max_length=32, editable=False)),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model, cloudy.projects.models.DeploymentVariablesContainer),
        ),
        migrations.CreateModel(
            name='DeploymentBaseVariables',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, verbose_name='variables name', db_index=True)),
                ('variables_format', models.CharField(default=b'yaml', max_length=32, verbose_name='deployment variables format', choices=[(b'yaml', b'YAML'), (b'json', b'JSON'), (b'python', b'Python'), (b'shell', b'Shell')])),
                ('variables', models.TextField(verbose_name='deployment variables', blank=True)),
                ('deleted', models.BooleanField(default=False, db_index=True, editable=False)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model, cloudy.projects.models.DeploymentVariablesContainer),
        ),
        migrations.CreateModel(
            name='DeploymentLogEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('source_url', models.TextField(help_text=b'the combined repository type, URL and commit', verbose_name='deployment source')),
                ('type', models.CharField(max_length=255)),
                ('text', models.TextField(null=True)),
            ],
            options={
                'ordering': ['-date'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='node name')),
                ('last_deployment_status', models.CharField(default=b'unknown', max_length=16, verbose_name='last deployment status', choices=[(b'unknown', b'Unknown'), (b'pending', b'Pending'), (b'success', b'Success'), (b'error', b'Error')])),
                ('last_deployment_output', models.TextField(null=True, verbose_name='last deployment output')),
                ('last_deployed_source_url', models.TextField(help_text=b'The last commit that was deployed, successfully or not.', null=True, verbose_name='last deployed commit')),
                ('last_deployment_date', models.DateTimeField(null=True, verbose_name='last deployment date')),
                ('client_version', models.CharField(max_length=32, null=True, verbose_name=b'cloudy client version')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('last_seen', models.DateTimeField(auto_now=True, db_index=True)),
                ('deployment', models.ForeignKey(related_name='nodes', to='projects.Deployment')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='project name')),
                ('key', models.CharField(default=cloudy.projects.models.uuid_hex, verbose_name='key', max_length=32, editable=False, db_index=True)),
                ('repository_type', models.CharField(default=b'git', max_length=255, verbose_name='repository type', choices=[(b'git', b'Git')])),
                ('repository_url', models.CharField(max_length=2047, verbose_name='repository URL')),
                ('deployment_script_type', models.CharField(default=b'bash', max_length=32, verbose_name='deployment script type', choices=[(b'bash', b'Bash script'), (b'python_script', b'Python script'), (b'python_entry_point', b'Python entry point (path.to.module or path.to.module:function)'), (b'python_file', b'Path to a python file')])),
                ('deployment_script', models.TextField(help_text=b'The script will be executed after the repository checkout, in the checkout directory.', verbose_name='deployment script', blank=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='node',
            unique_together=set([('deployment', 'name')]),
        ),
        migrations.AddField(
            model_name='deploymentlogentry',
            name='node',
            field=models.ForeignKey(to='projects.Node'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='deployment',
            name='base_variables',
            field=models.ForeignKey(blank=True, to='projects.DeploymentBaseVariables', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='deployment',
            name='project',
            field=models.ForeignKey(related_name='deployments', to='projects.Project'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='deployment',
            unique_together=set([('project', 'name')]),
        ),
    ]
