# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carnatic', '0004_concert_collection'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='concert',
            name='bootleg',
        ),
    ]
