# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('makam', '0008_instrumentperformance_attributes'),
    ]

    operations = [
        migrations.AddField(
            model_name='makam',
            name='mu2_name',
            field=models.CharField(max_length=250, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='makam',
            name='symtr_key',
            field=models.CharField(max_length=250, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='makam',
            name='tonic_symbol',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
