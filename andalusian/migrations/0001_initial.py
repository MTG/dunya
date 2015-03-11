# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import andalusian.models
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mbid', django_extensions.db.fields.UUIDField(max_length=36, null=True, editable=False, blank=True)),
                ('title', models.CharField(max_length=255)),
                ('transliterated_title', models.CharField(max_length=255, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(andalusian.models.AndalusianStyle, models.Model),
        ),
        migrations.CreateModel(
            name='AlbumRecording',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('track', models.IntegerField()),
                ('album', models.ForeignKey(to='andalusian.Album')),
            ],
            options={
                'ordering': ('track',),
            },
        ),
        migrations.CreateModel(
            name='AlbumType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=255)),
                ('transliterated_type', models.CharField(max_length=255, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('transliterated_name', models.CharField(max_length=200, blank=True)),
                ('mbid', django_extensions.db.fields.UUIDField(max_length=36, null=True, editable=False, blank=True)),
                ('gender', models.CharField(blank=True, max_length=1, null=True, choices=[(b'M', b'Male'), (b'F', b'Female')])),
                ('begin', models.CharField(max_length=10, null=True, blank=True)),
                ('end', models.CharField(max_length=10, null=True, blank=True)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('images', models.ManyToManyField(related_name='andalusian_artist_image_set', to='data.Image')),
                ('references', models.ManyToManyField(related_name='andalusian_artist_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='andalusian_artist_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(andalusian.models.AndalusianStyle, models.Model),
        ),
        migrations.CreateModel(
            name='ArtistAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('artist', models.ForeignKey(related_name='aliases', to='andalusian.Artist')),
            ],
        ),
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('transliterated_name', models.CharField(max_length=50, blank=True)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FormType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, blank=True)),
                ('transliterated_name', models.CharField(max_length=100, blank=True)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('images', models.ManyToManyField(related_name='andalusian_genre_image_set', to='data.Image')),
                ('references', models.ManyToManyField(related_name='andalusian_genre_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='andalusian_genre_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(andalusian.models.AndalusianStyle, models.Model),
        ),
        migrations.CreateModel(
            name='Instrument',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('percussion', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=50)),
                ('original_name', models.CharField(max_length=50, blank=True)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('images', models.ManyToManyField(related_name='andalusian_instrument_image_set', to='data.Image')),
                ('references', models.ManyToManyField(related_name='andalusian_instrument_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='andalusian_instrument_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(andalusian.models.AndalusianStyle, models.Model),
        ),
        migrations.CreateModel(
            name='InstrumentPerformance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lead', models.BooleanField(default=False)),
                ('instrument', models.ForeignKey(to='andalusian.Instrument')),
                ('performer', models.ForeignKey(to='andalusian.Artist')),
            ],
        ),
        migrations.CreateModel(
            name='InstrumentSectionPerformance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lead', models.BooleanField(default=False)),
                ('instrument', models.ForeignKey(to='andalusian.Instrument')),
                ('performer', models.ForeignKey(to='andalusian.Artist')),
            ],
        ),
        migrations.CreateModel(
            name='Mizan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, blank=True)),
                ('transliterated_name', models.CharField(max_length=50, blank=True)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('images', models.ManyToManyField(related_name='andalusian_mizan_image_set', to='data.Image')),
                ('references', models.ManyToManyField(related_name='andalusian_mizan_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='andalusian_mizan_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MusicalSchool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('transliterated_name', models.CharField(max_length=100, blank=True)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('images', models.ManyToManyField(related_name='andalusian_musicalschool_image_set', to='data.Image')),
                ('references', models.ManyToManyField(related_name='andalusian_musicalschool_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='andalusian_musicalschool_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(andalusian.models.AndalusianStyle, models.Model),
        ),
        migrations.CreateModel(
            name='Nawba',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, blank=True)),
                ('transliterated_name', models.CharField(max_length=50, blank=True)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('images', models.ManyToManyField(related_name='andalusian_nawba_image_set', to='data.Image')),
                ('references', models.ManyToManyField(related_name='andalusian_nawba_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='andalusian_nawba_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Orchestra',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mbid', django_extensions.db.fields.UUIDField(max_length=36, null=True, editable=False, blank=True)),
                ('name', models.CharField(max_length=255)),
                ('transliterated_name', models.CharField(max_length=255, blank=True)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(andalusian.models.AndalusianStyle, models.Model),
        ),
        migrations.CreateModel(
            name='OrchestraAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('orchestra', models.ForeignKey(related_name='aliases', to='andalusian.Orchestra')),
            ],
        ),
        migrations.CreateModel(
            name='OrchestraPerformer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('director', models.BooleanField(default=False)),
                ('begin', models.CharField(max_length=10, null=True, blank=True)),
                ('end', models.CharField(max_length=10, null=True, blank=True)),
                ('instruments', models.ManyToManyField(to='andalusian.Instrument')),
                ('orchestra', models.ForeignKey(to='andalusian.Orchestra')),
                ('performer', models.ForeignKey(to='andalusian.Artist')),
            ],
        ),
        migrations.CreateModel(
            name='Poem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.CharField(max_length=100, null=True, blank=True)),
                ('first_words', models.CharField(max_length=255, null=True, blank=True)),
                ('transliterated_first_words', models.CharField(max_length=255, null=True, blank=True)),
                ('text', models.TextField()),
                ('transliterated_text', models.TextField(blank=True)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('images', models.ManyToManyField(related_name='andalusian_poem_image_set', to='data.Image')),
                ('references', models.ManyToManyField(related_name='andalusian_poem_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='andalusian_poem_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PoemType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Recording',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mbid', django_extensions.db.fields.UUIDField(max_length=36, null=True, editable=False, blank=True)),
                ('title', models.CharField(max_length=255)),
                ('transliterated_title', models.CharField(max_length=255, blank=True)),
                ('length', models.IntegerField(null=True, blank=True)),
                ('year', models.IntegerField(null=True, blank=True)),
                ('artists', models.ManyToManyField(to='andalusian.Artist', through='andalusian.InstrumentPerformance')),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('genre', models.ForeignKey(to='andalusian.Genre', null=True)),
                ('images', models.ManyToManyField(related_name='andalusian_recording_image_set', to='data.Image')),
                ('references', models.ManyToManyField(related_name='andalusian_recording_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='andalusian_recording_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(andalusian.models.AndalusianStyle, models.Model),
        ),
        migrations.CreateModel(
            name='RecordingWork',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sequence', models.IntegerField()),
                ('recording', models.ForeignKey(to='andalusian.Recording')),
            ],
            options={
                'ordering': ('sequence',),
            },
        ),
        migrations.CreateModel(
            name='Sanaa',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('transliterated_title', models.CharField(max_length=255, blank=True)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('images', models.ManyToManyField(related_name='andalusian_sanaa_image_set', to='data.Image')),
                ('references', models.ManyToManyField(related_name='andalusian_sanaa_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='andalusian_sanaa_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_time', models.TimeField(null=True, blank=True)),
                ('end_time', models.TimeField(null=True, blank=True)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('form', models.ForeignKey(blank=True, to='andalusian.Form', null=True)),
                ('images', models.ManyToManyField(related_name='andalusian_section_image_set', to='data.Image')),
                ('mizan', models.ForeignKey(blank=True, to='andalusian.Mizan', null=True)),
                ('nawba', models.ForeignKey(blank=True, to='andalusian.Nawba', null=True)),
                ('recording', models.ForeignKey(to='andalusian.Recording')),
                ('references', models.ManyToManyField(related_name='andalusian_section_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='andalusian_section_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(andalusian.models.AndalusianStyle, models.Model),
        ),
        migrations.CreateModel(
            name='SectionSanaaPoem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order_number', models.IntegerField(null=True, blank=True)),
                ('poem', models.ForeignKey(to='andalusian.Poem')),
                ('sanaa', models.ForeignKey(to='andalusian.Sanaa')),
                ('section', models.ForeignKey(to='andalusian.Section')),
            ],
        ),
        migrations.CreateModel(
            name='Tab',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('transliterated_name', models.CharField(max_length=50, blank=True)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('images', models.ManyToManyField(related_name='andalusian_tab_image_set', to='data.Image')),
                ('references', models.ManyToManyField(related_name='andalusian_tab_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='andalusian_tab_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Work',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mbid', django_extensions.db.fields.UUIDField(max_length=36, null=True, editable=False, blank=True)),
                ('title', models.CharField(max_length=255)),
                ('transliterated_title', models.CharField(max_length=255, blank=True)),
                ('description', models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True)),
                ('images', models.ManyToManyField(related_name='andalusian_work_image_set', to='data.Image')),
                ('references', models.ManyToManyField(related_name='andalusian_work_reference_set', to='data.Source', blank=True)),
                ('source', models.ForeignKey(related_name='andalusian_work_source_set', blank=True, to='data.Source', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(andalusian.models.AndalusianStyle, models.Model),
        ),
        migrations.AddField(
            model_name='section',
            name='tab',
            field=models.ForeignKey(blank=True, to='andalusian.Tab', null=True),
        ),
        migrations.AddField(
            model_name='recordingwork',
            name='work',
            field=models.ForeignKey(to='andalusian.Work'),
        ),
        migrations.AddField(
            model_name='recording',
            name='works',
            field=models.ManyToManyField(to='andalusian.Work', through='andalusian.RecordingWork'),
        ),
        migrations.AddField(
            model_name='poem',
            name='type',
            field=models.ForeignKey(blank=True, to='andalusian.PoemType', null=True),
        ),
        migrations.AddField(
            model_name='orchestra',
            name='group_members',
            field=models.ManyToManyField(related_name='groups', through='andalusian.OrchestraPerformer', to='andalusian.Artist', blank=True),
        ),
        migrations.AddField(
            model_name='orchestra',
            name='images',
            field=models.ManyToManyField(related_name='andalusian_orchestra_image_set', to='data.Image'),
        ),
        migrations.AddField(
            model_name='orchestra',
            name='references',
            field=models.ManyToManyField(related_name='andalusian_orchestra_reference_set', to='data.Source', blank=True),
        ),
        migrations.AddField(
            model_name='orchestra',
            name='school',
            field=models.ForeignKey(blank=True, to='andalusian.MusicalSchool', null=True),
        ),
        migrations.AddField(
            model_name='orchestra',
            name='source',
            field=models.ForeignKey(related_name='andalusian_orchestra_source_set', blank=True, to='data.Source', null=True),
        ),
        migrations.AddField(
            model_name='instrumentsectionperformance',
            name='section',
            field=models.ForeignKey(to='andalusian.Section'),
        ),
        migrations.AddField(
            model_name='instrumentperformance',
            name='recording',
            field=models.ForeignKey(to='andalusian.Recording'),
        ),
        migrations.AddField(
            model_name='form',
            name='form_type',
            field=models.ForeignKey(blank=True, to='andalusian.FormType', null=True),
        ),
        migrations.AddField(
            model_name='form',
            name='images',
            field=models.ManyToManyField(related_name='andalusian_form_image_set', to='data.Image'),
        ),
        migrations.AddField(
            model_name='form',
            name='references',
            field=models.ManyToManyField(related_name='andalusian_form_reference_set', to='data.Source', blank=True),
        ),
        migrations.AddField(
            model_name='form',
            name='source',
            field=models.ForeignKey(related_name='andalusian_form_source_set', blank=True, to='data.Source', null=True),
        ),
        migrations.AddField(
            model_name='albumrecording',
            name='recording',
            field=models.ForeignKey(to='andalusian.Recording'),
        ),
        migrations.AddField(
            model_name='album',
            name='album_type',
            field=models.ForeignKey(blank=True, to='andalusian.AlbumType', null=True),
        ),
        migrations.AddField(
            model_name='album',
            name='artists',
            field=models.ManyToManyField(to='andalusian.Orchestra'),
        ),
        migrations.AddField(
            model_name='album',
            name='description',
            field=models.ForeignKey(related_name='+', blank=True, to='data.Description', null=True),
        ),
        migrations.AddField(
            model_name='album',
            name='director',
            field=models.ForeignKey(to='andalusian.Artist', null=True),
        ),
        migrations.AddField(
            model_name='album',
            name='images',
            field=models.ManyToManyField(related_name='andalusian_album_image_set', to='data.Image'),
        ),
        migrations.AddField(
            model_name='album',
            name='recordings',
            field=models.ManyToManyField(to='andalusian.Recording', through='andalusian.AlbumRecording'),
        ),
        migrations.AddField(
            model_name='album',
            name='references',
            field=models.ManyToManyField(related_name='andalusian_album_reference_set', to='data.Source', blank=True),
        ),
        migrations.AddField(
            model_name='album',
            name='source',
            field=models.ForeignKey(related_name='andalusian_album_source_set', blank=True, to='data.Source', null=True),
        ),
    ]
