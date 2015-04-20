# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kvedit', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='field',
            name='item',
            field=models.ForeignKey(related_name='fields', to='kvedit.Item'),
        ),
        migrations.AlterField(
            model_name='item',
            name='category',
            field=models.ForeignKey(related_name='items', to='kvedit.Category'),
        ),
    ]
