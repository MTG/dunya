# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators

class Migration(migrations.Migration):

    dependencies = [
        ('docserver', '0005_auto_20150729_1721'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentCollection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('root_directory', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=200)),
                ('collections', models.ManyToManyField(to='docserver.Collection')),
            ],
        ),
        migrations.AddField(
            model_name='document',
            name='rel_collections',
            field=models.ForeignKey(blank=True, to='docserver.DocumentCollection', null=True),
        ),

    ]
