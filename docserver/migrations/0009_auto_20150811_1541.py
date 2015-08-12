# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('docserver', '0008_auto_20150810_1121'),
    ]

    operations = [
        migrations.AddField(
            model_name='sourcefiletype',
            name='stype',
            field=models.CharField(blank=True, max_length=10, null=True, choices=[(b'audio', b'Audio'), (b'data', b'Data')]),
        ),
    ]
