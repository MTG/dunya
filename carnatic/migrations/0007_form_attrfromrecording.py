# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carnatic', '0006_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='form',
            name='attrfromrecording',
            field=models.BooleanField(default=False),
        ),
    ]
