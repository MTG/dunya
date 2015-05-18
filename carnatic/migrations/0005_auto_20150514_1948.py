# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carnatic', '0004_auto_20150514_1311'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecordingForm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sequence', models.IntegerField()),
                ('form', models.ForeignKey(to='carnatic.Form')),
                ('recording', models.ForeignKey(to='carnatic.Recording')),
            ],
            options={
                'ordering': ('sequence',),
            },
        ),
        migrations.AddField(
            model_name='recording',
            name='forms',
            field=models.ManyToManyField(to='carnatic.Form', through='carnatic.RecordingForm'),
        ),
    ]
