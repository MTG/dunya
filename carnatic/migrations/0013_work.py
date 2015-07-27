# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def forwards_func(apps, schema_editor):
    "Migration from old model to the new one."
    Recording = apps.get_model("carnatic", "Recording")
    RecordingWork = apps.get_model("carnatic", "RecordingWork")
    db_alias = schema_editor.connection.alias
    for r in Recording.objects.using(db_alias).exclude(work=None).all():
        RecordingWork.objects.create(recording_id=r.id, work_id=r.work.id, sequence=1)
        
def backwards_func(apps, schema_editor):
    "Migration from new model to the old one."
    RecordingWork = apps.get_model("carnatic", "RecordingWork")
    Recording = apps.get_model("carnatic", "Recording")
    Work = apps.get_model("carnatic", "Work")
    db_alias = schema_editor.connection.alias
    for w in RecordingWork.objects.using(db_alias).all():
        w.recording.work = w.work
        w.recording.save()
        w.delete()

class Migration(migrations.Migration):

    dependencies = [
        ('carnatic', '0012_auto_20150602_1401'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
            reverse_code=backwards_func
        ),
    ]
