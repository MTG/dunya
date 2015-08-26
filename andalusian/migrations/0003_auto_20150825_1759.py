# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('andalusian', '0002_auto_20150825_1727'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecordingPoem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order_number', models.IntegerField(null=True, blank=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='sectionsanaapoem',
            name='poem',
        ),
        migrations.RemoveField(
            model_name='sectionsanaapoem',
            name='sanaa',
        ),
        migrations.RemoveField(
            model_name='sectionsanaapoem',
            name='section',
        ),
        migrations.AddField(
            model_name='poem',
            name='title',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='recording',
            name='archive_url',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recording',
            name='musescore_url',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='SectionSanaaPoem',
        ),
        migrations.AddField(
            model_name='recordingpoem',
            name='poem',
            field=models.ForeignKey(to='andalusian.Poem'),
        ),
        migrations.AddField(
            model_name='recordingpoem',
            name='recording',
            field=models.ForeignKey(to='andalusian.Recording'),
        ),
    ]
