# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hindustani', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='releaserecording',
            name='disc',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='releaserecording',
            name='disctrack',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
