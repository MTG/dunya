# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('docserver', '0008_auto_20150814_1151'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='many_file',
            field=models.BooleanField(default=False),
        ),
    ]
