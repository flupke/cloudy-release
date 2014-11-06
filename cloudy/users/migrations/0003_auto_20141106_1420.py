# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cloudy.utils


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20141105_1624'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='auth_key',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='secret',
            field=models.CharField(default=cloudy.utils.uuid_hex, max_length=32, db_index=True),
            preserve_default=True,
        ),
    ]
