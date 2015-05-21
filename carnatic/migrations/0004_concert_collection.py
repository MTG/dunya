# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0002_collection'),
        ('carnatic', '0003_artist_description_edited'),
    ]

    operations = [
        migrations.AddField(
            model_name='concert',
            name='collection',
            field=models.ForeignKey(blank=True, to='data.Collection', null=True),
        ),
    ]
