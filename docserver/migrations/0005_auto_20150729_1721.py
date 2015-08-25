# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('docserver', '0004_auto_20150729_1014'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collection',
            name='restricted',
        ),
    ]
