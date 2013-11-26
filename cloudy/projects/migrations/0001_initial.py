# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Project'
        db.create_table(u'projects_project', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('key', self.gf('django.db.models.fields.CharField')(default='f6a535c3ff624b6a85e0b59bce6804ba', max_length=32, db_index=True)),
            ('repository_type', self.gf('django.db.models.fields.CharField')(default='git', max_length=255)),
            ('repository_url', self.gf('django.db.models.fields.TextField')()),
            ('commit', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('deploy_script_type', self.gf('django.db.models.fields.CharField')(default='bash', max_length=32)),
            ('deploy_script', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal(u'projects', ['Project'])

        # Adding model 'Deployment'
        db.create_table(u'projects_deployment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='deployments', to=orm['projects.Project'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('key', self.gf('django.db.models.fields.CharField')(default='e507655f258f404dae4682c1945c7271', max_length=32, db_index=True)),
            ('base_dir', self.gf('django.db.models.fields.TextField')()),
            ('variables_format', self.gf('django.db.models.fields.CharField')(default='yaml', max_length=32)),
            ('variables', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'projects', ['Deployment'])

        # Adding model 'Node'
        db.create_table(u'projects_node', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('deployment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Deployment'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('last_deployment_status', self.gf('django.db.models.fields.CharField')(max_length=16, null=True)),
            ('last_deployment_output', self.gf('django.db.models.fields.TextField')(null=True)),
            ('last_deployed_source_url', self.gf('django.db.models.fields.TextField')(null=True)),
            ('last_deployment_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'projects', ['Node'])

        # Adding unique constraint on 'Node', fields ['deployment', 'name']
        db.create_unique(u'projects_node', ['deployment_id', 'name'])

        # Adding model 'DeploymentLogEntry'
        db.create_table(u'projects_deploymentlogentry', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('deployment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Deployment'])),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Node'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('source_url', self.gf('django.db.models.fields.TextField')()),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('text', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal(u'projects', ['DeploymentLogEntry'])


    def backwards(self, orm):
        # Removing unique constraint on 'Node', fields ['deployment', 'name']
        db.delete_unique(u'projects_node', ['deployment_id', 'name'])

        # Deleting model 'Project'
        db.delete_table(u'projects_project')

        # Deleting model 'Deployment'
        db.delete_table(u'projects_deployment')

        # Deleting model 'Node'
        db.delete_table(u'projects_node')

        # Deleting model 'DeploymentLogEntry'
        db.delete_table(u'projects_deploymentlogentry')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'projects.deployment': {
            'Meta': {'ordering': "['-date_created']", 'object_name': 'Deployment'},
            'base_dir': ('django.db.models.fields.TextField', [], {}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'default': "'46481252c0de470ea810e677dc7461b7'", 'max_length': '32', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'deployments'", 'to': u"orm['projects.Project']"}),
            'variables': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'variables_format': ('django.db.models.fields.CharField', [], {'default': "'yaml'", 'max_length': '32'})
        },
        u'projects.deploymentlogentry': {
            'Meta': {'object_name': 'DeploymentLogEntry'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deployment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Deployment']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Node']"}),
            'source_url': ('django.db.models.fields.TextField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'projects.node': {
            'Meta': {'unique_together': "(('deployment', 'name'),)", 'object_name': 'Node'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deployment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Deployment']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_deployed_source_url': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'last_deployment_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'last_deployment_output': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'last_deployment_status': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'projects.project': {
            'Meta': {'ordering': "['-date_created']", 'object_name': 'Project'},
            'commit': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'deploy_script': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'deploy_script_type': ('django.db.models.fields.CharField', [], {'default': "'bash'", 'max_length': '32'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'default': "'9a9850cb39e4429bb62fd5826d82dda6'", 'max_length': '32', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'repository_type': ('django.db.models.fields.CharField', [], {'default': "'git'", 'max_length': '255'}),
            'repository_url': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['projects']