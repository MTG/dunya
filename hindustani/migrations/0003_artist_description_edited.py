# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hindustani', '0002_auto_20150319_1516'),
    ]

    operations = [
        migrations.AddField(
            model_name='artist',
            name='description_edited',
            field=models.BooleanField(default=False),
        ),
    ]
