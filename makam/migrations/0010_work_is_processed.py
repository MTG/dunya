# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('makam', '0009_auto_20160120_1830'),
    ]

    operations = [
        migrations.AddField(
            model_name='work',
            name='is_processed',
            field=models.BooleanField(default=False),
        ),
    ]
