# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators

def forwards_func(apps, schema_editor):
    "Migration from old model to the new one."
    Document = apps.get_model("docserver", "Document")
    DocumentCollection = apps.get_model("docserver", "DocumentCollection")
    db_alias = schema_editor.connection.alias
    for d in Document.objects.using(db_alias).all():
        coll = d.collection
        doc_c, created = DocumentCollection.objects.get_or_create(name=coll.name, root_directory=coll.root_directory)
        if created:
            doc_c.collections.add(coll)
        d.rel_collection = doc_c
        d.save()
        
def backwards_func(apps, schema_editor):
    "Migration from new model to the old one."
    Document = apps.get_model("docserver", "Document")
    DocumentCollection = apps.get_model("docserver", "DocumentCollection")
    db_alias = schema_editor.connection.alias
    for d in Document.objects.using(db_alias).all():
        coll = d.rel_collections.collections[0]
        d.collection = coll
        coll.root_directory = d.rel_collections.root_directory
        coll.save()
        d.save()

class Migration(migrations.Migration):

    dependencies = [
        ('docserver', '0005_auto_20150729_1721'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentCollection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('root_directory', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=200)),
                ('collections', models.ManyToManyField(to='docserver.Collection')),
            ],
        ),
        migrations.AddField(
            model_name='document',
            name='rel_collections',
            field=models.ForeignKey(blank=True, to='docserver.DocumentCollection', null=True),
        ),
        migrations.RunPython(
            forwards_func,
            reverse_code=backwards_func
        ),

    ]
