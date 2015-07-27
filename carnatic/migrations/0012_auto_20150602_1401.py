# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carnatic', '0011_auto_20150602_1352'),
    ]

    operations = [
        migrations.RenameField(
            model_name='work',
            old_name='raaga_new',
            new_name='raaga',
        ),
        migrations.RenameField(
            model_name='work',
            old_name='taala_new',
            new_name='taala',
        ),
    ]
