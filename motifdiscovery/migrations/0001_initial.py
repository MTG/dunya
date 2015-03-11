# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('filename', models.CharField(max_length=1000)),
                ('mbid', django_extensions.db.fields.UUIDField(max_length=36, null=True, editable=False, blank=True)),
                ('hasseed', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('distance', models.FloatField()),
                ('version', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Pattern',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_time', models.FloatField()),
                ('end_time', models.FloatField()),
                ('pair_id', models.IntegerField(null=True, blank=True)),
                ('isseed', models.IntegerField()),
                ('file', models.ForeignKey(to='motifdiscovery.File')),
            ],
        ),
        migrations.CreateModel(
            name='Segment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rounded_start', models.FloatField()),
                ('rounded_end', models.FloatField()),
                ('segment_path', models.CharField(max_length=500)),
                ('file', models.ForeignKey(to='motifdiscovery.File')),
            ],
        ),
        migrations.AddField(
            model_name='pattern',
            name='segment',
            field=models.ForeignKey(related_name='patterns', blank=True, to='motifdiscovery.Segment', null=True),
        ),
        migrations.AddField(
            model_name='match',
            name='source',
            field=models.ForeignKey(related_name='match_sources', to='motifdiscovery.Pattern'),
        ),
        migrations.AddField(
            model_name='match',
            name='target',
            field=models.ForeignKey(related_name='match_targets', to='motifdiscovery.Pattern'),
        ),
    ]
