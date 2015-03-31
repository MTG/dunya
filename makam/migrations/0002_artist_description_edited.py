# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('makam', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='artist',
            name='description_edited',
            field=models.BooleanField(default=False),
        ),
    ]
