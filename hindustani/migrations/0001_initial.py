# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-19 15:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import hindustani.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('mbid', models.UUIDField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, choices=[(b'M', b'Male'), (b'F', b'Female')], max_length=1, null=True)),
                ('begin', models.CharField(blank=True, max_length=10, null=True)),
                ('end', models.CharField(blank=True, max_length=10, null=True)),
                ('artist_type', models.CharField(choices=[(b'P', b'Person'), (b'G', b'Group')], default=b'P', max_length=1)),
                ('dummy', models.BooleanField(db_index=True, default=False)),
                ('description_edited', models.BooleanField(default=False)),
                ('description', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='data.Description')),
                ('group_members', models.ManyToManyField(blank=True, related_name='groups', to='hindustani.Artist')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.CharField(max_length=100)),
                ('primary', models.BooleanField(default=False)),
                ('locale', models.CharField(blank=True, max_length=10, null=True)),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aliases', to='hindustani.Artist')),
            ],
            options={
                'abstract': False,
            },
            bases=(hindustani.models.HindustaniStyle, models.Model),
        ),
        migrations.CreateModel(
            name='Composer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('mbid', models.UUIDField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, choices=[(b'M', b'Male'), (b'F', b'Female')], max_length=1, null=True)),
                ('begin', models.CharField(blank=True, max_length=10, null=True)),
                ('end', models.CharField(blank=True, max_length=10, null=True)),
                ('description', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='data.Description')),
                ('images', models.ManyToManyField(related_name='hindustani_composer_image_set', to='data.Image')),
                ('references', models.ManyToManyField(blank=True, related_name='hindustani_composer_reference_set', to='data.Source')),
                ('source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hindustani_composer_source_set', to='data.Source')),
            ],
            options={
                'abstract': False,
            },
            bases=(hindustani.models.HindustaniStyle, models.Model),
        ),
        migrations.CreateModel(
            name='ComposerAlias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.CharField(max_length=100)),
                ('primary', models.BooleanField(default=False)),
                ('locale', models.CharField(blank=True, max_length=10, null=True)),
                ('composer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aliases', to='hindustani.Composer')),
            ],
            options={
                'abstract': False,
            },
            bases=(hindustani.models.HindustaniStyle, models.Model),
        ),
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('common_name', models.CharField(max_length=50)),
                ('uuid', models.UUIDField(db_index=True)),
                ('description', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='data.Description')),
                ('images', models.ManyToManyField(related_name='hindustani_form_image_set', to='data.Image')),
                ('references', models.ManyToManyField(blank=True, related_name='hindustani_form_reference_set', to='data.Source')),
                ('source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hindustani_form_source_set', to='data.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FormAlias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aliases', to='hindustani.Form')),
            ],
        ),
        migrations.CreateModel(
            name='Instrument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percussion', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=50)),
                ('mbid', models.UUIDField(blank=True, null=True)),
                ('hidden', models.BooleanField(default=False)),
                ('description', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='data.Description')),
                ('images', models.ManyToManyField(related_name='hindustani_instrument_image_set', to='data.Image')),
                ('references', models.ManyToManyField(blank=True, related_name='hindustani_instrument_reference_set', to='data.Source')),
                ('source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hindustani_instrument_source_set', to='data.Source')),
            ],
            options={
                'abstract': False,
            },
            bases=(hindustani.models.HindustaniStyle, models.Model),
        ),
        migrations.CreateModel(
            name='InstrumentPerformance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lead', models.BooleanField(default=False)),
                ('attributes', models.CharField(blank=True, max_length=200, null=True)),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hindustani.Artist')),
                ('instrument', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hindustani.Instrument')),
            ],
            options={
                'abstract': False,
            },
            bases=(hindustani.models.HindustaniStyle, models.Model),
        ),
        migrations.CreateModel(
            name='Laya',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('common_name', models.CharField(max_length=50)),
                ('uuid', models.UUIDField(db_index=True)),
                ('description', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='data.Description')),
                ('images', models.ManyToManyField(related_name='hindustani_laya_image_set', to='data.Image')),
                ('references', models.ManyToManyField(blank=True, related_name='hindustani_laya_reference_set', to='data.Source')),
                ('source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hindustani_laya_source_set', to='data.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LayaAlias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('laya', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aliases', to='hindustani.Laya')),
            ],
        ),
        migrations.CreateModel(
            name='Lyrics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lyrics', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Raag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('common_name', models.CharField(max_length=50)),
                ('uuid', models.UUIDField(db_index=True)),
                ('description', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='data.Description')),
                ('images', models.ManyToManyField(related_name='hindustani_raag_image_set', to='data.Image')),
                ('references', models.ManyToManyField(blank=True, related_name='hindustani_raag_reference_set', to='data.Source')),
                ('source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hindustani_raag_source_set', to='data.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RaagAlias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('raag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aliases', to='hindustani.Raag')),
            ],
        ),
        migrations.CreateModel(
            name='Recording',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('mbid', models.UUIDField(blank=True, null=True)),
                ('length', models.IntegerField(blank=True, null=True)),
                ('description', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='data.Description')),
            ],
            options={
                'abstract': False,
            },
            bases=(hindustani.models.HindustaniStyle, models.Model),
        ),
        migrations.CreateModel(
            name='RecordingForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence', models.IntegerField()),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hindustani.Form')),
                ('recording', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hindustani.Recording')),
            ],
        ),
        migrations.CreateModel(
            name='RecordingLaya',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence', models.IntegerField()),
                ('laya', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hindustani.Laya')),
                ('recording', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hindustani.Recording')),
            ],
        ),
        migrations.CreateModel(
            name='RecordingRaag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence', models.IntegerField()),
                ('raag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hindustani.Raag')),
                ('recording', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hindustani.Recording')),
            ],
        ),
        migrations.CreateModel(
            name='RecordingSection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence', models.IntegerField()),
                ('recording', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hindustani.Recording')),
            ],
        ),
        migrations.CreateModel(
            name='RecordingTaal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence', models.IntegerField()),
                ('recording', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hindustani.Recording')),
            ],
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mbid', models.UUIDField(blank=True, null=True)),
                ('title', models.CharField(max_length=100)),
                ('artistcredit', models.CharField(max_length=255)),
                ('year', models.IntegerField(blank=True, null=True)),
                ('status', models.CharField(blank=True, max_length=100, null=True)),
                ('rel_type', models.CharField(blank=True, max_length=100, null=True)),
                ('artists', models.ManyToManyField(related_name='primary_concerts', to='hindustani.Artist')),
                ('collection', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hindustani_releases', to='data.Collection')),
                ('description', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='data.Description')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('track', models.IntegerField()),
                ('disc', models.IntegerField()),
                ('disctrack', models.IntegerField()),
                ('recording', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hindustani.Recording')),
                ('release', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hindustani.Release')),
            ],
            options={
                'ordering': ('track',),
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('common_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='SectionAlias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aliases', to='hindustani.Section')),
            ],
        ),
        migrations.CreateModel(
            name='Taal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('common_name', models.CharField(max_length=50)),
                ('num_maatras', models.IntegerField(null=True)),
                ('uuid', models.UUIDField(db_index=True)),
                ('description', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='data.Description')),
                ('images', models.ManyToManyField(related_name='hindustani_taal_image_set', to='data.Image')),
                ('references', models.ManyToManyField(blank=True, related_name='hindustani_taal_reference_set', to='data.Source')),
                ('source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hindustani_taal_source_set', to='data.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TaalAlias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('taal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aliases', to='hindustani.Taal')),
            ],
        ),
        migrations.CreateModel(
            name='Work',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('mbid', models.UUIDField(blank=True, null=True)),
                ('composers', models.ManyToManyField(blank=True, related_name='works', to='hindustani.Composer')),
                ('description', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='data.Description')),
                ('images', models.ManyToManyField(related_name='hindustani_work_image_set', to='data.Image')),
                ('lyricists', models.ManyToManyField(blank=True, related_name='lyric_works', to='hindustani.Composer')),
                ('lyrics', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hindustani.Lyrics')),
                ('references', models.ManyToManyField(blank=True, related_name='hindustani_work_reference_set', to='data.Source')),
                ('source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hindustani_work_source_set', to='data.Source')),
            ],
            options={
                'abstract': False,
            },
            bases=(hindustani.models.HindustaniStyle, models.Model),
        ),
        migrations.CreateModel(
            name='WorkTime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence', models.IntegerField()),
                ('time', models.IntegerField(blank=True, null=True)),
                ('recording', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hindustani.Recording')),
                ('work', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hindustani.Work')),
            ],
        ),
        migrations.AddField(
            model_name='release',
            name='recordings',
            field=models.ManyToManyField(through='hindustani.ReleaseRecording', to='hindustani.Recording'),
        ),
        migrations.AddField(
            model_name='release',
            name='references',
            field=models.ManyToManyField(blank=True, related_name='hindustani_release_reference_set', to='data.Source'),
        ),
        migrations.AddField(
            model_name='release',
            name='source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hindustani_release_source_set', to='data.Source'),
        ),
        migrations.AddField(
            model_name='recordingtaal',
            name='taal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hindustani.Taal'),
        ),
        migrations.AddField(
            model_name='recordingsection',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hindustani.Section'),
        ),
        migrations.AddField(
            model_name='recording',
            name='forms',
            field=models.ManyToManyField(through='hindustani.RecordingForm', to='hindustani.Form'),
        ),
        migrations.AddField(
            model_name='recording',
            name='images',
            field=models.ManyToManyField(related_name='hindustani_recording_image_set', to='data.Image'),
        ),
        migrations.AddField(
            model_name='recording',
            name='layas',
            field=models.ManyToManyField(through='hindustani.RecordingLaya', to='hindustani.Laya'),
        ),
        migrations.AddField(
            model_name='recording',
            name='performance',
            field=models.ManyToManyField(through='hindustani.InstrumentPerformance', to='hindustani.Artist'),
        ),
        migrations.AddField(
            model_name='recording',
            name='raags',
            field=models.ManyToManyField(through='hindustani.RecordingRaag', to='hindustani.Raag'),
        ),
        migrations.AddField(
            model_name='recording',
            name='references',
            field=models.ManyToManyField(blank=True, related_name='hindustani_recording_reference_set', to='data.Source'),
        ),
        migrations.AddField(
            model_name='recording',
            name='sections',
            field=models.ManyToManyField(through='hindustani.RecordingSection', to='hindustani.Section'),
        ),
        migrations.AddField(
            model_name='recording',
            name='source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hindustani_recording_source_set', to='data.Source'),
        ),
        migrations.AddField(
            model_name='recording',
            name='taals',
            field=models.ManyToManyField(through='hindustani.RecordingTaal', to='hindustani.Taal'),
        ),
        migrations.AddField(
            model_name='recording',
            name='works',
            field=models.ManyToManyField(through='hindustani.WorkTime', to='hindustani.Work'),
        ),
        migrations.AddField(
            model_name='instrumentperformance',
            name='recording',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hindustani.Recording'),
        ),
        migrations.AddField(
            model_name='artist',
            name='main_instrument',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hindustani.Instrument'),
        ),
        migrations.AddField(
            model_name='artist',
            name='references',
            field=models.ManyToManyField(blank=True, related_name='hindustani_artist_reference_set', to='data.Source'),
        ),
        migrations.AddField(
            model_name='artist',
            name='source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hindustani_artist_source_set', to='data.Source'),
        ),
    ]
