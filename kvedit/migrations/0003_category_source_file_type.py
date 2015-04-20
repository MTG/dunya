# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('docserver', '0003_auto_20150313_0920'),
        ('kvedit', '0002_auto_20150411_0213'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='source_file_type',
            field=models.ForeignKey(blank=True, to='docserver.SourceFileType', null=True),
        ),
    ]
