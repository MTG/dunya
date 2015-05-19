# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectionfile',
            name='file_md5',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
