# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_deployment_acl_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deployment',
            name='acl_type',
            field=models.SmallIntegerField(default=0, choices=[(0, b'Public'), (1, b'Public read, ACL write'), (2, b'ACL read and write')]),
            preserve_default=True,
        ),
    ]
