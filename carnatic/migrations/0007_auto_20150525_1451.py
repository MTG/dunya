# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carnatic', '0006_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecordingRaaga',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sequence', models.IntegerField(null=True, blank=True)),
                ('raaga', models.ForeignKey(to='carnatic.Raaga')),
            ],
        ),
        migrations.CreateModel(
            name='RecordingTaala',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sequence', models.IntegerField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='RecordingWork',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sequence', models.IntegerField(null=True, blank=True)),
            ],
        ),
        migrations.AlterField(
            model_name='recording',
            name='work',
            field=models.ForeignKey(related_name='single_work', blank=True, to='carnatic.Work', null=True),
        ),
        migrations.AddField(
            model_name='recordingwork',
            name='recording',
            field=models.ForeignKey(to='carnatic.Recording'),
        ),
        migrations.AddField(
            model_name='recordingwork',
            name='work',
            field=models.ForeignKey(to='carnatic.Work'),
        ),
        migrations.AddField(
            model_name='recordingtaala',
            name='recording',
            field=models.ForeignKey(to='carnatic.Recording'),
        ),
        migrations.AddField(
            model_name='recordingtaala',
            name='taala',
            field=models.ForeignKey(to='carnatic.Taala'),
        ),
        migrations.AddField(
            model_name='recordingraaga',
            name='recording',
            field=models.ForeignKey(to='carnatic.Recording'),
        ),
        migrations.AddField(
            model_name='recording',
            name='raagas',
            field=models.ManyToManyField(to='carnatic.Raaga', through='carnatic.RecordingRaaga'),
        ),
        migrations.AddField(
            model_name='recording',
            name='taalas',
            field=models.ManyToManyField(to='carnatic.Taala', through='carnatic.RecordingTaala'),
        ),
        migrations.AddField(
            model_name='recording',
            name='works',
            field=models.ManyToManyField(to='carnatic.Work', through='carnatic.RecordingWork'),
        ),
    ]
