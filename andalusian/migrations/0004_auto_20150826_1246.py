# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('andalusian', '0003_auto_20150825_1759'),
    ]

    operations = [
        migrations.AddField(
            model_name='poem',
            name='transliterated_title',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='recording',
            name='poems',
            field=models.ManyToManyField(to='andalusian.Poem', through='andalusian.RecordingPoem'),
        ),
    ]
