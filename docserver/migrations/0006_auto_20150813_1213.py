# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators

def forwards_func(apps, schema_editor):
     "Migration from old model to the new one."
     Document = apps.get_model("docserver", "Document")
     Collection = apps.get_model("docserver", "Collection")
     db_alias = schema_editor.connection.alias
     for d in Document.objects.using(db_alias).all():
         d.collections.add(d.collection)

def backwards_func(apps, schema_editor):
     "Migration from new model to the old one."
     Document = apps.get_model("docserver", "Document")
     Collection = apps.get_model("docserver", "Collection")
     db_alias = schema_editor.connection.alias
     for d in Document.objects.using(db_alias).all():
         coll = d.collections[0]
         d.collection = coll
         coll.save()
 
class Migration(migrations.Migration):

    dependencies = [
        ('docserver', '0005_auto_20150729_1721'),
    ]

    operations = [
        migrations.RenameField(
            model_name='collectionpermission',
            old_name='rate_limit',
            new_name='streamable',
        ),
        migrations.AddField(
            model_name='document',
            name='collections',
            field=models.ManyToManyField(to='docserver.Collection'),
        ),
        migrations.AddField(
            model_name='sourcefiletype',
            name='stype',
            field=models.CharField(default='data', max_length=10, choices=[(b'audio', b'Audio'), (b'data', b'Data')]),
            preserve_default=False,
        ),
        migrations.RunPython(
            forwards_func,
            reverse_code=backwards_func
        ),
    ]
