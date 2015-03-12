# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('docserver', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sourcefiletype',
            name='mimetype',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sourcefiletype',
            name='slug',
            field=models.SlugField(default=''),
            preserve_default=False,
        ),
    ]
