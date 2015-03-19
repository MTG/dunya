# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carnatic', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='concertrecording',
            name='disc',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='concertrecording',
            name='disctrack',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
