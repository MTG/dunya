# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import carnatic.models
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
                ('group_members', models.ManyToManyField(related_name='groups', to='carnatic.Artist', blank=True)),
                ('gurus', models.ManyToManyField(related_name='students', to='carnatic.Artist')),
                ('images', models.ManyToManyField(related_name='carnatic_artist_image_set', to='data.Image')),
            ],
            options={
                'abstract': False,
            },
            bases=(carnatic.models.CarnaticStyle, models.Model),
        ),
        migrations.CreateModel(
            name='ArtistAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alias', models.CharField(max_length=100)),
                ('primary', models.BooleanField(default=False)),
                ('locale', models.CharField(max_length=10, null=True, blank=True)),
                ('artist', models.ForeignKey(related_name='aliases', to='carnatic.Artist')),
            ],
            options={
                'abstract': False,
            },
            bases=(carnatic.models.CarnaticStyle, models.Model),
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
                ('images', models.ManyToManyField(related_name='carnatic_composer_image_set', to='data.Image')),
                ('references', models.ManyToManyField(related_name='carnatic_composer_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='carnatic_composer_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(carnatic.models.CarnaticStyle, models.Model),
        ),
        migrations.CreateModel(
            name='ComposerAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alias', models.CharField(max_length=100)),
                ('primary', models.BooleanField(default=False)),
                ('locale', models.CharField(max_length=10, null=True, blank=True)),
                ('composer', models.ForeignKey(related_name='aliases', to='carnatic.Composer')),
            ],
            options={
                'abstract': False,
            },
            bases=(carnatic.models.CarnaticStyle, models.Model),
        ),
        migrations.CreateModel(
            name='Concert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mbid', django_extensions.db.fields.UUIDField(max_length=36, null=True, editable=False, blank=True)),
                ('title', models.CharField(max_length=100)),
                ('artistcredit', models.CharField(max_length=255)),
                ('year', models.IntegerField(null=True, blank=True)),
                ('bootleg', models.BooleanField(default=False)),
                ('artists', models.ManyToManyField(related_name='primary_concerts', to='carnatic.Artist')),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('images', models.ManyToManyField(related_name='carnatic_concert_image_set', to='data.Image')),
            ],
            options={
                'abstract': False,
            },
            bases=(carnatic.models.CarnaticStyle, models.Model),
        ),
        migrations.CreateModel(
            name='ConcertRecording',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('track', models.IntegerField()),
                ('concert', models.ForeignKey(to='carnatic.Concert')),
            ],
            options={
                'ordering': ('track',),
            },
        ),
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='FormAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('form', models.ForeignKey(related_name='aliases', to='carnatic.Form')),
            ],
        ),
        migrations.CreateModel(
            name='GeographicRegion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
            bases=(carnatic.models.CarnaticStyle, models.Model),
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
                ('images', models.ManyToManyField(related_name='carnatic_instrument_image_set', to='data.Image')),
                ('references', models.ManyToManyField(related_name='carnatic_instrument_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='carnatic_instrument_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(carnatic.models.CarnaticStyle, models.Model),
        ),
        migrations.CreateModel(
            name='InstrumentAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('instrument', models.ForeignKey(related_name='aliases', to='carnatic.Instrument')),
            ],
            options={
                'abstract': False,
            },
            bases=(carnatic.models.CarnaticStyle, models.Model),
        ),
        migrations.CreateModel(
            name='InstrumentPerformance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lead', models.BooleanField(default=False)),
                ('artist', models.ForeignKey(to='carnatic.Artist')),
                ('instrument', models.ForeignKey(blank=True, to='carnatic.Instrument', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(carnatic.models.CarnaticStyle, models.Model),
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            bases=(carnatic.models.CarnaticStyle, models.Model),
        ),
        migrations.CreateModel(
            name='LanguageAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('language', models.ForeignKey(related_name='aliases', to='carnatic.Language')),
            ],
            bases=(carnatic.models.CarnaticStyle, models.Model),
        ),
        migrations.CreateModel(
            name='MusicalSchool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
            bases=(carnatic.models.CarnaticStyle, models.Model),
        ),
        migrations.CreateModel(
            name='Raaga',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('common_name', models.CharField(max_length=50)),
                ('uuid', django_extensions.db.fields.UUIDField(db_index=True, max_length=36, editable=False, blank=True)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('images', models.ManyToManyField(related_name='carnatic_raaga_image_set', to='data.Image')),
                ('references', models.ManyToManyField(related_name='carnatic_raaga_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='carnatic_raaga_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RaagaAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('raaga', models.ForeignKey(related_name='aliases', to='carnatic.Raaga')),
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
                ('images', models.ManyToManyField(related_name='carnatic_recording_image_set', to='data.Image')),
                ('performance', models.ManyToManyField(to='carnatic.Artist', through='carnatic.InstrumentPerformance')),
                ('references', models.ManyToManyField(related_name='carnatic_recording_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='carnatic_recording_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(carnatic.models.CarnaticStyle, models.Model),
        ),
        migrations.CreateModel(
            name='Sabbah',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
            ],
            bases=(carnatic.models.CarnaticStyle, models.Model),
        ),
        migrations.CreateModel(
            name='Taala',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('common_name', models.CharField(max_length=50)),
                ('num_aksharas', models.IntegerField(null=True)),
                ('uuid', django_extensions.db.fields.UUIDField(db_index=True, max_length=36, editable=False, blank=True)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('images', models.ManyToManyField(related_name='carnatic_taala_image_set', to='data.Image')),
                ('references', models.ManyToManyField(related_name='carnatic_taala_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='carnatic_taala_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TaalaAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('taala', models.ForeignKey(related_name='aliases', to='carnatic.Taala')),
            ],
        ),
        migrations.CreateModel(
            name='Work',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('mbid', django_extensions.db.fields.UUIDField(max_length=36, null=True, editable=False, blank=True)),
                ('composers', models.ManyToManyField(related_name='works', to='carnatic.Composer', blank=True)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('form', models.ForeignKey(blank=True, to='carnatic.Form', null=True)),
                ('images', models.ManyToManyField(related_name='carnatic_work_image_set', to='data.Image')),
                ('language', models.ForeignKey(blank=True, to='carnatic.Language', null=True)),
                ('lyricists', models.ManyToManyField(related_name='lyric_works', to='carnatic.Composer', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(carnatic.models.CarnaticStyle, models.Model),
        ),
        migrations.CreateModel(
            name='WorkRaaga',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sequence', models.IntegerField(null=True, blank=True)),
                ('raaga', models.ForeignKey(to='carnatic.Raaga')),
                ('work', models.ForeignKey(to='carnatic.Work')),
            ],
        ),
        migrations.CreateModel(
            name='WorkTaala',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sequence', models.IntegerField(null=True, blank=True)),
                ('taala', models.ForeignKey(to='carnatic.Taala')),
                ('work', models.ForeignKey(to='carnatic.Work')),
            ],
        ),
        migrations.AddField(
            model_name='work',
            name='raaga',
            field=models.ManyToManyField(to='carnatic.Raaga', through='carnatic.WorkRaaga'),
        ),
        migrations.AddField(
            model_name='work',
            name='references',
            field=models.ManyToManyField(related_name='carnatic_work_reference_set', to='data.Source', blank=True),
        ),
        migrations.AddField(
            model_name='work',
            name='source',
            field=models.ForeignKey(related_name='carnatic_work_source_set', blank=True, to='data.Source', null=True),
        ),
        migrations.AddField(
            model_name='work',
            name='taala',
            field=models.ManyToManyField(to='carnatic.Taala', through='carnatic.WorkTaala'),
        ),
        migrations.AddField(
            model_name='recording',
            name='work',
            field=models.ForeignKey(blank=True, to='carnatic.Work', null=True),
        ),
        migrations.AddField(
            model_name='instrumentperformance',
            name='recording',
            field=models.ForeignKey(to='carnatic.Recording'),
        ),
        migrations.AddField(
            model_name='concertrecording',
            name='recording',
            field=models.ForeignKey(to='carnatic.Recording'),
        ),
        migrations.AddField(
            model_name='concert',
            name='recordings',
            field=models.ManyToManyField(to='carnatic.Recording', through='carnatic.ConcertRecording'),
        ),
        migrations.AddField(
            model_name='concert',
            name='references',
            field=models.ManyToManyField(related_name='carnatic_concert_reference_set', to='data.Source', blank=True),
        ),
        migrations.AddField(
            model_name='concert',
            name='sabbah',
            field=models.ForeignKey(blank=True, to='carnatic.Sabbah', null=True),
        ),
        migrations.AddField(
            model_name='concert',
            name='source',
            field=models.ForeignKey(related_name='carnatic_concert_source_set', blank=True, to='data.Source', null=True),
        ),
        migrations.AddField(
            model_name='composer',
            name='state',
            field=models.ForeignKey(blank=True, to='carnatic.GeographicRegion', null=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='main_instrument',
            field=models.ForeignKey(blank=True, to='carnatic.Instrument', null=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='references',
            field=models.ManyToManyField(related_name='carnatic_artist_reference_set', to='data.Source', blank=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='source',
            field=models.ForeignKey(related_name='carnatic_artist_source_set', blank=True, to='data.Source', null=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='state',
            field=models.ForeignKey(blank=True, to='carnatic.GeographicRegion', null=True),
        ),
    ]
