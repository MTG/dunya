# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_collectionfile_filesize'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collectiondirectorylogmessage',
            name='checker',
        ),
        migrations.RemoveField(
            model_name='collectiondirectorylogmessage',
            name='collectiondirectory',
        ),
        migrations.RemoveField(
            model_name='collectionfilelogmessage',
            name='checker',
        ),
        migrations.RemoveField(
            model_name='collectionfilelogmessage',
            name='collectionfile',
        ),
        migrations.RemoveField(
            model_name='collectionfileresult',
            name='checker',
        ),
        migrations.RemoveField(
            model_name='collectionfileresult',
            name='collectionfile',
        ),
        migrations.RemoveField(
            model_name='musicbrainzreleaseresult',
            name='checker',
        ),
        migrations.RemoveField(
            model_name='musicbrainzreleaseresult',
            name='musicbrainzrelease',
        ),
        migrations.RemoveField(
            model_name='collection',
            name='checkers',
        ),
        migrations.RemoveField(
            model_name='musicbrainzreleaselogmessage',
            name='checker',
        ),
        migrations.DeleteModel(
            name='CollectionDirectoryLogMessage',
        ),
        migrations.DeleteModel(
            name='CollectionFileLogMessage',
        ),
        migrations.DeleteModel(
            name='CollectionFileResult',
        ),
        migrations.DeleteModel(
            name='CompletenessChecker',
        ),
        migrations.DeleteModel(
            name='MusicbrainzReleaseResult',
        ),
    ]
