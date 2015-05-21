# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0002_collection'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='collection',
            options={'permissions': (('access_restricted', 'Can see restricted collections'),)},
        ),
        migrations.AddField(
            model_name='collection',
            name='mbid',
            field=django_extensions.db.fields.UUIDField(max_length=36, null=True, editable=False, blank=True),
        ),
    ]
