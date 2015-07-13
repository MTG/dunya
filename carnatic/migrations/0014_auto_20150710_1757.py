# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carnatic', '0013_work'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recording',
            name='work',
        ),
        migrations.AlterField(
            model_name='work',
            name='raaga',
            field=models.ForeignKey(blank=True, to='carnatic.Raaga', null=True),
        ),
        migrations.AlterField(
            model_name='work',
            name='taala',
            field=models.ForeignKey(blank=True, to='carnatic.Taala', null=True),
        ),
    ]
