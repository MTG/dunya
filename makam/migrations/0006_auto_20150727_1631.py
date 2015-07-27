# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('makam', '0005_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='recording',
            name='analyse',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='recording',
            name='artists',
            field=models.ManyToManyField(related_name='recordings_artist', to='makam.Artist'),
        ),
    ]
