# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('makam', '0007_auto_20150812_1615'),
    ]

    operations = [
        migrations.AddField(
            model_name='instrumentperformance',
            name='attributes',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
