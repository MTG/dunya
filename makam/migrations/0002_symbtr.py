# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('makam', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SymbTr',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('uuid', django_extensions.db.fields.UUIDField(db_index=True, max_length=36, editable=False, blank=True)),
            ],
        ),
    ]
