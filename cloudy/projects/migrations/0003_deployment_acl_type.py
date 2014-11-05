# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_deployment_acl'),
    ]

    operations = [
        migrations.AddField(
            model_name='deployment',
            name='acl_type',
            field=models.SmallIntegerField(default=0, choices=[(0, b'public'), (1, b'public read, ACL write'), (2, b'ACL read and write')]),
            preserve_default=True,
        ),
    ]
