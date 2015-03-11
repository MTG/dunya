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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('collectionid', django_extensions.db.fields.UUIDField(max_length=36, editable=False, blank=True)),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField()),
                ('description', models.CharField(max_length=200)),
                ('root_directory', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='DerivedFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('outputname', models.CharField(max_length=50)),
                ('extension', models.CharField(max_length=10)),
                ('mimetype', models.CharField(max_length=100)),
                ('computation_time', models.IntegerField(null=True, blank=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='DerivedFilePart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('part_order', models.IntegerField()),
                ('path', models.CharField(max_length=500)),
                ('size', models.IntegerField()),
                ('derivedfile', models.ForeignKey(related_name='parts', to='docserver.DerivedFile')),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=500)),
                ('external_identifier', models.CharField(max_length=200, null=True, blank=True)),
                ('collection', models.ForeignKey(related_name='documents', to='docserver.Collection')),
            ],
        ),
        migrations.CreateModel(
            name='DocumentLogMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.CharField(max_length=20)),
                ('message', models.TextField()),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('document', models.ForeignKey(related_name='logs', to='docserver.Document')),
            ],
            options={
                'ordering': ['-datetime'],
            },
        ),
        migrations.CreateModel(
            name='EssentiaVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.CharField(max_length=200)),
                ('sha1', models.CharField(max_length=200)),
                ('commit_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField()),
                ('depends', models.CharField(max_length=100, null=True, blank=True)),
                ('module', models.CharField(max_length=200)),
                ('disabled', models.BooleanField(default=False)),
                ('collections', models.ManyToManyField(to='docserver.Collection')),
            ],
        ),
        migrations.CreateModel(
            name='ModuleVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.CharField(max_length=10)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('module', models.ForeignKey(related_name='versions', to='docserver.Module')),
            ],
        ),
        migrations.CreateModel(
            name='PyCompmusicVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sha1', models.CharField(max_length=200)),
                ('commit_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='SourceFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(max_length=500)),
                ('size', models.IntegerField()),
                ('document', models.ForeignKey(related_name='sourcefiles', to='docserver.Document')),
            ],
        ),
        migrations.CreateModel(
            name='SourceFileType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('extension', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Worker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hostname', models.CharField(max_length=200)),
                ('state', models.CharField(default=b'0', max_length=1, choices=[(b'0', b'New'), (b'1', b'Updating'), (b'2', b'Updated')])),
                ('essentia', models.ForeignKey(blank=True, to='docserver.EssentiaVersion', null=True)),
                ('pycompmusic', models.ForeignKey(blank=True, to='docserver.PyCompmusicVersion', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='sourcefile',
            name='file_type',
            field=models.ForeignKey(to='docserver.SourceFileType'),
        ),
        migrations.AddField(
            model_name='module',
            name='source_type',
            field=models.ForeignKey(to='docserver.SourceFileType'),
        ),
        migrations.AddField(
            model_name='documentlogmessage',
            name='moduleversion',
            field=models.ForeignKey(blank=True, to='docserver.ModuleVersion', null=True),
        ),
        migrations.AddField(
            model_name='documentlogmessage',
            name='sourcefile',
            field=models.ForeignKey(blank=True, to='docserver.SourceFile', null=True),
        ),
        migrations.AddField(
            model_name='derivedfile',
            name='derived_from',
            field=models.ForeignKey(to='docserver.SourceFile'),
        ),
        migrations.AddField(
            model_name='derivedfile',
            name='document',
            field=models.ForeignKey(related_name='derivedfiles', to='docserver.Document'),
        ),
        migrations.AddField(
            model_name='derivedfile',
            name='essentia',
            field=models.ForeignKey(blank=True, to='docserver.EssentiaVersion', null=True),
        ),
        migrations.AddField(
            model_name='derivedfile',
            name='module_version',
            field=models.ForeignKey(to='docserver.ModuleVersion'),
        ),
        migrations.AddField(
            model_name='derivedfile',
            name='pycompmusic',
            field=models.ForeignKey(blank=True, to='docserver.PyCompmusicVersion', null=True),
        ),
    ]
