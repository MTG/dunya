# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('permission', models.CharField(default=b'S', max_length=1, choices=[(b'S', b'Staff-only'), (b'R', b'Restricted'), (b'U', b'Unrestricted')])),
                ('name', models.CharField(max_length=100)),
            ],
        ),
    ]
