# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_auto_20141106_1420'),
        ('logs', '0003_auto_20141107_1206'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='logentry',
            options={'ordering': ['-timestamp']},
        ),
        migrations.AddField(
            model_name='logentry',
            name='deployment',
            field=models.ForeignKey(related_name='logs', to='projects.Deployment', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='logentry',
            name='project',
            field=models.ForeignKey(related_name='logs', to='projects.Project', null=True),
            preserve_default=True,
        ),
    ]
