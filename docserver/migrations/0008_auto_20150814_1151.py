# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('docserver', '0007_auto_20150813_1217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sourcefiletype',
            name='slug',
            field=models.SlugField(validators=[django.core.validators.RegexValidator(regex=b'^[a-z0-9-]+$', message=b'Slug can only contain a-z 0-9 and -')]),
        ),
    ]
