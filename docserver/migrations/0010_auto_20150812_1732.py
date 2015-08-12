# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('docserver', '0009_auto_20150811_1541'),
    ]

    operations = [
        migrations.RenameField(
            model_name='collectionpermission',
            old_name='rate_limit',
            new_name='streamable',
        ),
        migrations.AlterField(
            model_name='sourcefiletype',
            name='stype',
            field=models.CharField(default='data', max_length=10, choices=[(b'audio', b'Audio'), (b'data', b'Data')]),
            preserve_default=False,
        ),
    ]
