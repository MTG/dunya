# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('docserver', '0010_auto_20150819_1319'),
        ('kvedit', '0004_item_reverify'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='collection',
            field=models.ForeignKey(blank=True, to='docserver.Collection', null=True),
        ),
    ]
