# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', django_extensions.db.fields.UUIDField(max_length=36, serialize=False, editable=False, primary_key=True, blank=True)),
                ('name', models.CharField(max_length=200)),
                ('last_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('root_directory', models.CharField(max_length=255)),
                ('do_import', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='CollectionDirectory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(max_length=500)),
                ('collection', models.ForeignKey(to='dashboard.Collection')),
            ],
        ),
        migrations.CreateModel(
            name='CollectionDirectoryLogMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField()),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['-datetime'],
            },
        ),
        migrations.CreateModel(
            name='CollectionFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('recordingid', django_extensions.db.fields.UUIDField(max_length=36, null=True, editable=False, blank=True)),
                ('directory', models.ForeignKey(to='dashboard.CollectionDirectory')),
            ],
        ),
        migrations.CreateModel(
            name='CollectionFileLogMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField()),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['-datetime'],
            },
        ),
        migrations.CreateModel(
            name='CollectionFileResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('result', models.CharField(max_length=10, choices=[(b'g', b'Good'), (b'b', b'Bad')])),
                ('data', models.TextField(null=True, blank=True)),
            ],
            options={
                'ordering': ['-datetime'],
            },
        ),
        migrations.CreateModel(
            name='CollectionFileState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', models.CharField(default=b'n', max_length=10, choices=[(b'n', b'Not started'), (b'i', b'Importing'), (b'f', b'Finished'), (b'e', b'Error')])),
                ('state_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('collectionfile', models.ForeignKey(to='dashboard.CollectionFile')),
            ],
            options={
                'ordering': ['-state_date'],
            },
        ),
        migrations.CreateModel(
            name='CollectionLogMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField()),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('collection', models.ForeignKey(to='dashboard.Collection')),
            ],
            options={
                'ordering': ['-datetime'],
            },
        ),
        migrations.CreateModel(
            name='CollectionState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', models.CharField(default=b'n', max_length=10, choices=[(b'n', b'Not started'), (b's', b'Scanning'), (b'd', b'Scanned'), (b'i', b'Importing'), (b'f', b'Finished'), (b'e', b'Error')])),
                ('state_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('collection', models.ForeignKey(to='dashboard.Collection')),
            ],
            options={
                'ordering': ['-state_date'],
            },
        ),
        migrations.CreateModel(
            name='CompletenessChecker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('module', models.CharField(max_length=200)),
                ('templatefile', models.CharField(max_length=200, null=True, blank=True)),
                ('type', models.CharField(max_length=5, choices=[(b'r', b'Release'), (b'f', b'File')])),
            ],
        ),
        migrations.CreateModel(
            name='MusicbrainzRelease',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mbid', django_extensions.db.fields.UUIDField(max_length=36, editable=False, blank=True)),
                ('title', models.CharField(max_length=200)),
                ('artist', models.CharField(max_length=200, null=True, blank=True)),
                ('ignore', models.BooleanField(default=False)),
                ('collection', models.ForeignKey(to='dashboard.Collection')),
            ],
        ),
        migrations.CreateModel(
            name='MusicbrainzReleaseLogMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField()),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('checker', models.ForeignKey(blank=True, to='dashboard.CompletenessChecker', null=True)),
                ('musicbrainzrelease', models.ForeignKey(to='dashboard.MusicbrainzRelease')),
            ],
            options={
                'ordering': ['-datetime'],
            },
        ),
        migrations.CreateModel(
            name='MusicbrainzReleaseResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('result', models.CharField(max_length=10, choices=[(b'g', b'Good'), (b'b', b'Bad')])),
                ('data', models.TextField(null=True, blank=True)),
                ('checker', models.ForeignKey(to='dashboard.CompletenessChecker')),
                ('musicbrainzrelease', models.ForeignKey(blank=True, to='dashboard.MusicbrainzRelease', null=True)),
            ],
            options={
                'ordering': ['-datetime'],
            },
        ),
        migrations.CreateModel(
            name='MusicbrainzReleaseState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', models.CharField(default=b'n', max_length=10, choices=[(b'n', b'Not started'), (b'i', b'Importing'), (b'f', b'Finished'), (b'e', b'Error')])),
                ('state_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('musicbrainzrelease', models.ForeignKey(to='dashboard.MusicbrainzRelease')),
            ],
            options={
                'ordering': ['-state_date'],
            },
        ),
        migrations.AddField(
            model_name='collectionfileresult',
            name='checker',
            field=models.ForeignKey(to='dashboard.CompletenessChecker'),
        ),
        migrations.AddField(
            model_name='collectionfileresult',
            name='collectionfile',
            field=models.ForeignKey(to='dashboard.CollectionFile'),
        ),
        migrations.AddField(
            model_name='collectionfilelogmessage',
            name='checker',
            field=models.ForeignKey(blank=True, to='dashboard.CompletenessChecker', null=True),
        ),
        migrations.AddField(
            model_name='collectionfilelogmessage',
            name='collectionfile',
            field=models.ForeignKey(to='dashboard.CollectionFile'),
        ),
        migrations.AddField(
            model_name='collectiondirectorylogmessage',
            name='checker',
            field=models.ForeignKey(blank=True, to='dashboard.CompletenessChecker', null=True),
        ),
        migrations.AddField(
            model_name='collectiondirectorylogmessage',
            name='collectiondirectory',
            field=models.ForeignKey(to='dashboard.CollectionDirectory'),
        ),
        migrations.AddField(
            model_name='collectiondirectory',
            name='musicbrainzrelease',
            field=models.ForeignKey(blank=True, to='dashboard.MusicbrainzRelease', null=True),
        ),
        migrations.AddField(
            model_name='collection',
            name='checkers',
            field=models.ManyToManyField(to='dashboard.CompletenessChecker'),
        ),
        migrations.AlterUniqueTogether(
            name='musicbrainzrelease',
            unique_together=set([('mbid', 'collection')]),
        ),
    ]
