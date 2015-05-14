# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('makam', '0003_artist_description_edited'),
    ]

    operations = [
        migrations.AddField(
            model_name='release',
            name='rel_type',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='release',
            name='status',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
