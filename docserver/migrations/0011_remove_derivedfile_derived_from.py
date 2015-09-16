# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('docserver', '0010_auto_20150819_1319'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='derivedfile',
            name='derived_from',
        ),
    ]
