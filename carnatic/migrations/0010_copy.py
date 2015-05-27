# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def forwards_func(apps, schema_editor):
    "Migration from old model to the new one."
    Work = apps.get_model("carnatic", "Work")
    db_alias = schema_editor.connection.alias
    for w in Work.objects.using(db_alias).all():
        if len(w.raaga.all()):
            w.raaga_new = w.raaga.all()[0]
            w.save()
        if len(w.taala.all()):
            w.taala_new = w.taala.all()[0]
            w.save()

def backwards_func(apps, schema_editor):
    "Migration from new model to the old one."
    Work = apps.get_model("carnatic", "Work")
    db_alias = schema_editor.connection.alias
    for w in Work.objects.using(db_alias).all():
        if len(w.raaga.all()):
            w.raaga.append(w.raaga_new) 
            w.save()
        if len(w.taala.all()):
            w.taala.append(taala_new)
            w.save()

class Migration(migrations.Migration):

    dependencies = [
        ('carnatic', '0009_auto_20150527_1759'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
            reverse_code=backwards_func
        ),
    ]
