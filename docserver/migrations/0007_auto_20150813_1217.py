# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('docserver', '0006_auto_20150813_1213'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='collection',
        ),
        migrations.AlterField(
            model_name='document',
            name='collections',
            field=models.ManyToManyField(related_name='documents', to='docserver.Collection'),
        ),
    ]
