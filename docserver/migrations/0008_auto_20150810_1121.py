# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('docserver', '0007_auto_20150807_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentcollection',
            name='collections',
            field=models.ManyToManyField(related_name='rel_documents', to='docserver.Collection'),
        ),
        migrations.RemoveField(
            model_name='collection',
            name='root_directory',
        ),
        migrations.RemoveField(
            model_name='document',
            name='collection',
        ),
    ]
