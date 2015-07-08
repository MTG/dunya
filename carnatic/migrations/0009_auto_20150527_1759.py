# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carnatic', '0008_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='work',
            name='raaga_new',
            field=models.ForeignKey(related_name='new_raaga', blank=True, to='carnatic.Raaga', null=True),
        ),
        migrations.AddField(
            model_name='work',
            name='taala_new',
            field=models.ForeignKey(related_name='new_taala', blank=True, to='carnatic.Taala', null=True),
        ),
    ]
