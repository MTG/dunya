# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kvedit', '0003_category_source_file_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='reverify',
            field=models.BooleanField(default=False),
        ),
    ]
