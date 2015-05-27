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
            name='raaga_new',
        ),
        migrations.RemoveField(
            model_name='work',
            name='taala_new',
        ),
        migrations.RemoveField(
            model_name='work',
            name='raaga',
        ),
        migrations.AddField(
            model_name='work',
            name='raaga',
            field=models.ForeignKey(blank=True, to='carnatic.Raaga', null=True),
        ),
        migrations.RemoveField(
            model_name='work',
            name='taala',
        ),
        migrations.AddField(
            model_name='work',
            name='taala',
            field=models.ForeignKey(blank=True, to='carnatic.Taala', null=True),
        ),
    ]
