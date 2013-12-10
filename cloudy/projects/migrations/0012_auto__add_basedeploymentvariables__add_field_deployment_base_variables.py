# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BaseDeploymentVariables'
        db.create_table(u'projects_basedeploymentvariables', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
            ('variables_format', self.gf('django.db.models.fields.CharField')(default='yaml', max_length=32)),
            ('variables', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'projects', ['BaseDeploymentVariables'])

        # Adding field 'Deployment.base_variables'
        db.add_column(u'projects_deployment', 'base_variables',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.BaseDeploymentVariables'], null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'BaseDeploymentVariables'
        db.delete_table(u'projects_basedeploymentvariables')

        # Deleting field 'Deployment.base_variables'
        db.delete_column(u'projects_deployment', 'base_variables_id')


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
        u'projects.basedeploymentvariables': {
            'Meta': {'ordering': "['name']", 'object_name': 'BaseDeploymentVariables'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'variables': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'variables_format': ('django.db.models.fields.CharField', [], {'default': "'yaml'", 'max_length': '32'})
        },
        u'projects.deployment': {
            'Meta': {'ordering': "['-date_created']", 'unique_together': "(['project', 'name'],)", 'object_name': 'Deployment'},
            'base_dir': ('django.db.models.fields.CharField', [], {'max_length': '2047'}),
            'base_variables': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.BaseDeploymentVariables']", 'null': 'True'}),
            'commit': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'default': "'f5bf3894b0ad48b6a0c55e21ea2f6b6f'", 'max_length': '32', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'deployments'", 'to': u"orm['projects.Project']"}),
            'redeploy_bit': ('django.db.models.fields.CharField', [], {'default': "'b4bbabc1290c4fb2b2459fdb1338bcec'", 'max_length': '32'}),
            'variables': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'variables_format': ('django.db.models.fields.CharField', [], {'default': "'yaml'", 'max_length': '32'})
        },
        u'projects.deploymentlogentry': {
            'Meta': {'ordering': "['-date']", 'object_name': 'DeploymentLogEntry'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Node']"}),
            'source_url': ('django.db.models.fields.TextField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'projects.node': {
            'Meta': {'unique_together': "(('deployment', 'name'),)", 'object_name': 'Node'},
            'client_version': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deployment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'nodes'", 'to': u"orm['projects.Deployment']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_deployed_source_url': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'last_deployment_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'last_deployment_output': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'last_deployment_status': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '16'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'projects.project': {
            'Meta': {'ordering': "['name']", 'object_name': 'Project'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'deployment_script': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'deployment_script_type': ('django.db.models.fields.CharField', [], {'default': "'bash'", 'max_length': '32'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'default': "'7b0f2aab687c41cd9667064edb9c2857'", 'max_length': '32', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'repository_type': ('django.db.models.fields.CharField', [], {'default': "'git'", 'max_length': '255'}),
            'repository_url': ('django.db.models.fields.CharField', [], {'max_length': '2047'})
        }
    }

    complete_apps = ['projects']