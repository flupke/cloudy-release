# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_project_clean'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='clean',
        ),
        migrations.AddField(
            model_name='project',
            name='clean_repository',
            field=models.BooleanField(default=True, verbose_name='clean repository before deployments'),
            preserve_default=True,
        ),
    ]
