# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('docserver', '0002_auto_20150311_2252'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='collection',
            options={'permissions': (('read_restricted', 'Can read files in restricted collections'),)},
        ),
        migrations.AddField(
            model_name='collection',
            name='restricted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='module',
            name='restricted',
            field=models.BooleanField(default=False),
        ),
    ]
