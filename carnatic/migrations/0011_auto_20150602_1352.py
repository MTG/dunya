# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carnatic', '0010_copy'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='work',
            name='raaga',
        ),
        migrations.RemoveField(
            model_name='work',
            name='taala',
        ),
    ]
