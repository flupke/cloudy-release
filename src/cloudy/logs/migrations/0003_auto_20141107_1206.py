# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0002_logentry_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logentry',
            name='link',
            field=models.CharField(max_length=255, null=True, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='logentry',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
            preserve_default=True,
        ),
    ]
