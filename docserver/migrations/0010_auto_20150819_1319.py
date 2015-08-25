# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('docserver', '0009_module_many_file'),
    ]

    operations = [
        migrations.RenameField(
            model_name='module',
            old_name='many_file',
            new_name='many_files',
        ),
    ]
