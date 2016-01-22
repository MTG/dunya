# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('docserver', '0011_remove_derivedfile_derived_from'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='data',
            field=models.TextField(blank=True),
        ),
    ]
