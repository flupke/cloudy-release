# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_auto_20141106_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='clean',
            field=models.BooleanField(default=True, help_text=b'Clean repository before every deployment.', verbose_name='clean'),
            preserve_default=True,
        ),
    ]
