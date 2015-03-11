# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import hindustani.models
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
                ('group_members', models.ManyToManyField(related_name='groups', to='hindustani.Artist', blank=True)),
                ('images', models.ManyToManyField(related_name='hindustani_artist_image_set', to='data.Image')),
            ],
            options={
                'abstract': False,
            },
            bases=(hindustani.models.HindustaniStyle, models.Model),
        ),
        migrations.CreateModel(
            name='ArtistAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alias', models.CharField(max_length=100)),
                ('primary', models.BooleanField(default=False)),
                ('locale', models.CharField(max_length=10, null=True, blank=True)),
                ('artist', models.ForeignKey(related_name='aliases', to='hindustani.Artist')),
            ],
            options={
                'abstract': False,
            },
            bases=(hindustani.models.HindustaniStyle, models.Model),
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
                ('images', models.ManyToManyField(related_name='hindustani_composer_image_set', to='data.Image')),
                ('references', models.ManyToManyField(related_name='hindustani_composer_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='hindustani_composer_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(hindustani.models.HindustaniStyle, models.Model),
        ),
        migrations.CreateModel(
            name='ComposerAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alias', models.CharField(max_length=100)),
                ('primary', models.BooleanField(default=False)),
                ('locale', models.CharField(max_length=10, null=True, blank=True)),
                ('composer', models.ForeignKey(related_name='aliases', to='hindustani.Composer')),
            ],
            options={
                'abstract': False,
            },
            bases=(hindustani.models.HindustaniStyle, models.Model),
        ),
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('common_name', models.CharField(max_length=50)),
                ('uuid', django_extensions.db.fields.UUIDField(db_index=True, max_length=36, editable=False, blank=True)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('images', models.ManyToManyField(related_name='hindustani_form_image_set', to='data.Image')),
                ('references', models.ManyToManyField(related_name='hindustani_form_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='hindustani_form_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FormAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('form', models.ForeignKey(related_name='aliases', to='hindustani.Form')),
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
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('images', models.ManyToManyField(related_name='hindustani_instrument_image_set', to='data.Image')),
                ('references', models.ManyToManyField(related_name='hindustani_instrument_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='hindustani_instrument_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(hindustani.models.HindustaniStyle, models.Model),
        ),
        migrations.CreateModel(
            name='InstrumentPerformance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lead', models.BooleanField(default=False)),
                ('artist', models.ForeignKey(to='hindustani.Artist')),
                ('instrument', models.ForeignKey(blank=True, to='hindustani.Instrument', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(hindustani.models.HindustaniStyle, models.Model),
        ),
        migrations.CreateModel(
            name='Laya',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('common_name', models.CharField(max_length=50)),
                ('uuid', django_extensions.db.fields.UUIDField(db_index=True, max_length=36, editable=False, blank=True)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('images', models.ManyToManyField(related_name='hindustani_laya_image_set', to='data.Image')),
                ('references', models.ManyToManyField(related_name='hindustani_laya_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='hindustani_laya_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LayaAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('laya', models.ForeignKey(related_name='aliases', to='hindustani.Laya')),
            ],
        ),
        migrations.CreateModel(
            name='Lyrics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lyrics', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Raag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('common_name', models.CharField(max_length=50)),
                ('uuid', django_extensions.db.fields.UUIDField(db_index=True, max_length=36, editable=False, blank=True)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('images', models.ManyToManyField(related_name='hindustani_raag_image_set', to='data.Image')),
                ('references', models.ManyToManyField(related_name='hindustani_raag_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='hindustani_raag_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RaagAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('raag', models.ForeignKey(related_name='aliases', to='hindustani.Raag')),
            ],
        ),
        migrations.CreateModel(
            name='Recording',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('mbid', django_extensions.db.fields.UUIDField(max_length=36, null=True, editable=False, blank=True)),
                ('length', models.IntegerField(null=True, blank=True)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(hindustani.models.HindustaniStyle, models.Model),
        ),
        migrations.CreateModel(
            name='RecordingForm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sequence', models.IntegerField()),
                ('form', models.ForeignKey(to='hindustani.Form')),
                ('recording', models.ForeignKey(to='hindustani.Recording')),
            ],
        ),
        migrations.CreateModel(
            name='RecordingLaya',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sequence', models.IntegerField()),
                ('laya', models.ForeignKey(to='hindustani.Laya')),
                ('recording', models.ForeignKey(to='hindustani.Recording')),
            ],
        ),
        migrations.CreateModel(
            name='RecordingRaag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sequence', models.IntegerField()),
                ('raag', models.ForeignKey(to='hindustani.Raag')),
                ('recording', models.ForeignKey(to='hindustani.Recording')),
            ],
        ),
        migrations.CreateModel(
            name='RecordingSection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sequence', models.IntegerField()),
                ('recording', models.ForeignKey(to='hindustani.Recording')),
            ],
        ),
        migrations.CreateModel(
            name='RecordingTaal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sequence', models.IntegerField()),
                ('recording', models.ForeignKey(to='hindustani.Recording')),
            ],
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mbid', django_extensions.db.fields.UUIDField(max_length=36, null=True, editable=False, blank=True)),
                ('title', models.CharField(max_length=100)),
                ('artistcredit', models.CharField(max_length=255)),
                ('year', models.IntegerField(null=True, blank=True)),
                ('artists', models.ManyToManyField(related_name='primary_concerts', to='hindustani.Artist')),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('images', models.ManyToManyField(related_name='hindustani_release_image_set', to='data.Image')),
            ],
            options={
                'abstract': False,
            },
            bases=(hindustani.models.HindustaniStyle, models.Model),
        ),
        migrations.CreateModel(
            name='ReleaseRecording',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('track', models.IntegerField()),
                ('recording', models.ForeignKey(to='hindustani.Recording')),
                ('release', models.ForeignKey(to='hindustani.Release')),
            ],
            options={
                'ordering': ('track',),
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('common_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='SectionAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('section', models.ForeignKey(related_name='aliases', to='hindustani.Section')),
            ],
        ),
        migrations.CreateModel(
            name='Taal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('common_name', models.CharField(max_length=50)),
                ('num_maatras', models.IntegerField(null=True)),
                ('uuid', django_extensions.db.fields.UUIDField(db_index=True, max_length=36, editable=False, blank=True)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('images', models.ManyToManyField(related_name='hindustani_taal_image_set', to='data.Image')),
                ('references', models.ManyToManyField(related_name='hindustani_taal_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='hindustani_taal_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TaalAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('taal', models.ForeignKey(related_name='aliases', to='hindustani.Taal')),
            ],
        ),
        migrations.CreateModel(
            name='Work',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('mbid', django_extensions.db.fields.UUIDField(max_length=36, null=True, editable=False, blank=True)),
                ('composers', models.ManyToManyField(related_name='works', to='hindustani.Composer', blank=True)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('images', models.ManyToManyField(related_name='hindustani_work_image_set', to='data.Image')),
                ('lyricists', models.ManyToManyField(related_name='lyric_works', to='hindustani.Composer', blank=True)),
                ('lyrics', models.ForeignKey(blank=True, to='hindustani.Lyrics', null=True)),
                ('references', models.ManyToManyField(related_name='hindustani_work_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='hindustani_work_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(hindustani.models.HindustaniStyle, models.Model),
        ),
        migrations.CreateModel(
            name='WorkTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sequence', models.IntegerField()),
                ('time', models.IntegerField(null=True, blank=True)),
                ('recording', models.ForeignKey(to='hindustani.Recording')),
                ('work', models.ForeignKey(to='hindustani.Work')),
            ],
        ),
        migrations.AddField(
            model_name='release',
            name='recordings',
            field=models.ManyToManyField(to='hindustani.Recording', through='hindustani.ReleaseRecording'),
        ),
        migrations.AddField(
            model_name='release',
            name='references',
            field=models.ManyToManyField(related_name='hindustani_release_reference_set', to='data.Source', blank=True),
        ),
        migrations.AddField(
            model_name='release',
            name='source',
            field=models.ForeignKey(related_name='hindustani_release_source_set', blank=True, to='data.Source', null=True),
        ),
        migrations.AddField(
            model_name='recordingtaal',
            name='taal',
            field=models.ForeignKey(to='hindustani.Taal'),
        ),
        migrations.AddField(
            model_name='recordingsection',
            name='section',
            field=models.ForeignKey(to='hindustani.Section'),
        ),
        migrations.AddField(
            model_name='recording',
            name='forms',
            field=models.ManyToManyField(to='hindustani.Form', through='hindustani.RecordingForm'),
        ),
        migrations.AddField(
            model_name='recording',
            name='images',
            field=models.ManyToManyField(related_name='hindustani_recording_image_set', to='data.Image'),
        ),
        migrations.AddField(
            model_name='recording',
            name='layas',
            field=models.ManyToManyField(to='hindustani.Laya', through='hindustani.RecordingLaya'),
        ),
        migrations.AddField(
            model_name='recording',
            name='performance',
            field=models.ManyToManyField(to='hindustani.Artist', through='hindustani.InstrumentPerformance'),
        ),
        migrations.AddField(
            model_name='recording',
            name='raags',
            field=models.ManyToManyField(to='hindustani.Raag', through='hindustani.RecordingRaag'),
        ),
        migrations.AddField(
            model_name='recording',
            name='references',
            field=models.ManyToManyField(related_name='hindustani_recording_reference_set', to='data.Source', blank=True),
        ),
        migrations.AddField(
            model_name='recording',
            name='sections',
            field=models.ManyToManyField(to='hindustani.Section', through='hindustani.RecordingSection'),
        ),
        migrations.AddField(
            model_name='recording',
            name='source',
            field=models.ForeignKey(related_name='hindustani_recording_source_set', blank=True, to='data.Source', null=True),
        ),
        migrations.AddField(
            model_name='recording',
            name='taals',
            field=models.ManyToManyField(to='hindustani.Taal', through='hindustani.RecordingTaal'),
        ),
        migrations.AddField(
            model_name='recording',
            name='works',
            field=models.ManyToManyField(to='hindustani.Work', through='hindustani.WorkTime'),
        ),
        migrations.AddField(
            model_name='instrumentperformance',
            name='recording',
            field=models.ForeignKey(to='hindustani.Recording'),
        ),
        migrations.AddField(
            model_name='artist',
            name='main_instrument',
            field=models.ForeignKey(blank=True, to='hindustani.Instrument', null=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='references',
            field=models.ManyToManyField(related_name='hindustani_artist_reference_set', to='data.Source', blank=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='source',
            field=models.ForeignKey(related_name='hindustani_artist_source_set', blank=True, to='data.Source', null=True),
        ),
    ]
