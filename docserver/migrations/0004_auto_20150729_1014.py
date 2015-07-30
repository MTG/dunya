# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('docserver', '0003_auto_20150313_0920'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectionPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('permission', models.CharField(default=b'S', max_length=1, choices=[(b'S', b'Staff-only'), (b'R', b'Restricted'), (b'U', b'Unrestricted')])),
                ('rate_limit', models.BooleanField(default=False)),
                ('collection', models.ForeignKey(to='docserver.Collection')),
            ],
            options={
                'permissions': (('access_restricted_file', 'Can see restricted source files'),),
            },
        ),
        migrations.AddField(
            model_name='collectionpermission',
            name='source_type',
            field=models.ForeignKey(to='docserver.SourceFileType'),
        ),
    ]
