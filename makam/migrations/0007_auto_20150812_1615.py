# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('makam', '0006_auto_20150727_1631'),
    ]

    operations = [
        migrations.AlterField(
            model_name='symbtr',
            name='uuid',
            field=django_extensions.db.fields.UUIDField(max_length=36, editable=False, blank=True),
        ),
            migrations.RunSQL('alter table makam_symbtr alter COLUMN uuid type uuid USING ("uuid"::uuid)'),
        migrations.AlterField(
            model_name='symbtr',
            name='uuid',
            field=models.UUIDField(db_index=True),
        ),
    ]
