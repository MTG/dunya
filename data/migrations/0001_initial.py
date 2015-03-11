# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Description',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=b'images')),
                ('small_image', models.ImageField(null=True, upload_to=b'images', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('uri', models.CharField(max_length=255)),
                ('last_updated', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='SourceName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='VisitLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('user', models.CharField(max_length=100, null=True, blank=True)),
                ('ip', models.CharField(max_length=16)),
                ('path', models.CharField(max_length=256)),
            ],
        ),
        migrations.AddField(
            model_name='source',
            name='source_name',
            field=models.ForeignKey(to='data.SourceName'),
        ),
        migrations.AddField(
            model_name='image',
            name='source',
            field=models.ForeignKey(blank=True, to='data.Source', null=True),
        ),
        migrations.AddField(
            model_name='description',
            name='source',
            field=models.ForeignKey(blank=True, to='data.Source', null=True),
        ),
    ]
