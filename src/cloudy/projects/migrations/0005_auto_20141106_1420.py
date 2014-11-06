# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_auto_20141105_1646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deployment',
            name='acl',
            field=models.ManyToManyField(related_name='deployments', verbose_name=b'ACL', to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deployment',
            name='acl_type',
            field=models.SmallIntegerField(default=0, verbose_name=b'ACL type', choices=[(0, b'Public'), (1, b'Public read, ACL write'), (2, b'ACL read and write')]),
            preserve_default=True,
        ),
    ]
