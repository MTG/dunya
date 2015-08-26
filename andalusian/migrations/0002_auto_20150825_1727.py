# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('andalusian', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artistalias',
            name='name',
        ),
        migrations.AddField(
            model_name='artistalias',
            name='alias',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='artistalias',
            name='locale',
            field=models.CharField(max_length=10, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='artistalias',
            name='primary',
            field=models.BooleanField(default=False),
        ),
    ]
