# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import makam.models
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('mbid', django_extensions.db.fields.UUIDField(max_length=36, null=True, editable=False, blank=True)),
                ('gender', models.CharField(blank=True, max_length=1, null=True, choices=[(b'M', b'Male'), (b'F', b'Female')])),
                ('begin', models.CharField(max_length=10, null=True, blank=True)),
                ('end', models.CharField(max_length=10, null=True, blank=True)),
                ('artist_type', models.CharField(default=b'P', max_length=1, choices=[(b'P', b'Person'), (b'G', b'Group')])),
                ('dummy', models.BooleanField(default=False, db_index=True)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('group_members', models.ManyToManyField(related_name='groups', to='makam.Artist', blank=True)),
                ('images', models.ManyToManyField(related_name='makam_artist_image_set', to='data.Image')),
            ],
            options={
                'abstract': False,
            },
            bases=(makam.models.MakamStyle, models.Model),
        ),
        migrations.CreateModel(
            name='ArtistAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alias', models.CharField(max_length=100)),
                ('primary', models.BooleanField(default=False)),
                ('locale', models.CharField(max_length=10, null=True, blank=True)),
                ('artist', models.ForeignKey(related_name='aliases', to='makam.Artist')),
            ],
            options={
                'abstract': False,
            },
            bases=(makam.models.MakamStyle, models.Model),
        ),
        migrations.CreateModel(
            name='Composer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('mbid', django_extensions.db.fields.UUIDField(max_length=36, null=True, editable=False, blank=True)),
                ('gender', models.CharField(blank=True, max_length=1, null=True, choices=[(b'M', b'Male'), (b'F', b'Female')])),
                ('begin', models.CharField(max_length=10, null=True, blank=True)),
                ('end', models.CharField(max_length=10, null=True, blank=True)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('images', models.ManyToManyField(related_name='makam_composer_image_set', to='data.Image')),
                ('references', models.ManyToManyField(related_name='makam_composer_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='makam_composer_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(makam.models.MakamStyle, models.Model),
        ),
        migrations.CreateModel(
            name='ComposerAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alias', models.CharField(max_length=100)),
                ('primary', models.BooleanField(default=False)),
                ('locale', models.CharField(max_length=10, null=True, blank=True)),
                ('composer', models.ForeignKey(related_name='aliases', to='makam.Composer')),
            ],
            options={
                'abstract': False,
            },
            bases=(makam.models.MakamStyle, models.Model),
        ),
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('uuid', django_extensions.db.fields.UUIDField(db_index=True, max_length=36, editable=False, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='FormAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('form', models.ForeignKey(related_name='aliases', to='makam.Form')),
            ],
        ),
        migrations.CreateModel(
            name='Instrument',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('percussion', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=50)),
                ('mbid', django_extensions.db.fields.UUIDField(max_length=36, null=True, editable=False, blank=True)),
                ('hidden', models.BooleanField(default=False)),
                ('name_tr', models.CharField(max_length=50)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('images', models.ManyToManyField(related_name='makam_instrument_image_set', to='data.Image')),
                ('references', models.ManyToManyField(related_name='makam_instrument_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='makam_instrument_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(makam.models.MakamStyle, models.Model),
        ),
        migrations.CreateModel(
            name='InstrumentPerformance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lead', models.BooleanField(default=False)),
                ('artist', models.ForeignKey(to='makam.Artist')),
                ('instrument', models.ForeignKey(blank=True, to='makam.Instrument', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(makam.models.MakamStyle, models.Model),
        ),
        migrations.CreateModel(
            name='Makam',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('uuid', django_extensions.db.fields.UUIDField(db_index=True, max_length=36, editable=False, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='MakamAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('makam', models.ForeignKey(related_name='aliases', to='makam.Makam')),
            ],
        ),
        migrations.CreateModel(
            name='Recording',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('mbid', django_extensions.db.fields.UUIDField(max_length=36, null=True, editable=False, blank=True)),
                ('length', models.IntegerField(null=True, blank=True)),
                ('has_taksim', models.BooleanField(default=False)),
                ('has_gazel', models.BooleanField(default=False)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('images', models.ManyToManyField(related_name='makam_recording_image_set', to='data.Image')),
                ('makam', models.ManyToManyField(to='makam.Makam', blank=True)),
                ('performance', models.ManyToManyField(to='makam.Artist', through='makam.InstrumentPerformance')),
                ('references', models.ManyToManyField(related_name='makam_recording_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='makam_recording_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(makam.models.MakamStyle, models.Model),
        ),
        migrations.CreateModel(
            name='RecordingWork',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sequence', models.IntegerField()),
                ('recording', models.ForeignKey(to='makam.Recording')),
            ],
            options={
                'ordering': ('sequence',),
            },
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mbid', django_extensions.db.fields.UUIDField(max_length=36, null=True, editable=False, blank=True)),
                ('title', models.CharField(max_length=100)),
                ('artistcredit', models.CharField(max_length=255)),
                ('year', models.IntegerField(null=True, blank=True)),
                ('is_concert', models.BooleanField(default=False)),
                ('artists', models.ManyToManyField(related_name='primary_concerts', to='makam.Artist')),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('images', models.ManyToManyField(related_name='makam_release_image_set', to='data.Image')),
            ],
            options={
                'abstract': False,
            },
            bases=(makam.models.MakamStyle, models.Model),
        ),
        migrations.CreateModel(
            name='ReleaseRecording',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('track', models.IntegerField()),
                ('recording', models.ForeignKey(to='makam.Recording')),
                ('release', models.ForeignKey(to='makam.Release')),
            ],
            options={
                'ordering': ('track',),
            },
        ),
        migrations.CreateModel(
            name='Usul',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('uuid', django_extensions.db.fields.UUIDField(db_index=True, max_length=36, editable=False, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='UsulAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('usul', models.ForeignKey(related_name='aliases', to='makam.Usul')),
            ],
        ),
        migrations.CreateModel(
            name='Work',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('mbid', django_extensions.db.fields.UUIDField(max_length=36, null=True, editable=False, blank=True)),
                ('composition_date', models.CharField(max_length=100, null=True, blank=True)),
                ('composers', models.ManyToManyField(related_name='works', to='makam.Composer', blank=True)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('form', models.ManyToManyField(to='makam.Form', blank=True)),
                ('images', models.ManyToManyField(related_name='makam_work_image_set', to='data.Image')),
                ('lyricists', models.ManyToManyField(related_name='lyric_works', to='makam.Composer', blank=True)),
                ('makam', models.ManyToManyField(to='makam.Makam', blank=True)),
                ('references', models.ManyToManyField(related_name='makam_work_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='makam_work_source_set', blank=True, to='data.Source', null=True)),
                ('usul', models.ManyToManyField(to='makam.Usul', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(makam.models.MakamStyle, models.Model),
        ),
        migrations.AddField(
            model_name='release',
            name='recordings',
            field=models.ManyToManyField(to='makam.Recording', through='makam.ReleaseRecording'),
        ),
        migrations.AddField(
            model_name='release',
            name='references',
            field=models.ManyToManyField(related_name='makam_release_reference_set', to='data.Source', blank=True),
        ),
        migrations.AddField(
            model_name='release',
            name='source',
            field=models.ForeignKey(related_name='makam_release_source_set', blank=True, to='data.Source', null=True),
        ),
        migrations.AddField(
            model_name='recordingwork',
            name='work',
            field=models.ForeignKey(to='makam.Work'),
        ),
        migrations.AddField(
            model_name='recording',
            name='works',
            field=models.ManyToManyField(to='makam.Work', through='makam.RecordingWork'),
        ),
        migrations.AddField(
            model_name='instrumentperformance',
            name='recording',
            field=models.ForeignKey(to='makam.Recording'),
        ),
        migrations.AddField(
            model_name='artist',
            name='main_instrument',
            field=models.ForeignKey(blank=True, to='makam.Instrument', null=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='references',
            field=models.ManyToManyField(related_name='makam_artist_reference_set', to='data.Source', blank=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='source',
            field=models.ForeignKey(related_name='makam_artist_source_set', blank=True, to='data.Source', null=True),
        ),
    ]
