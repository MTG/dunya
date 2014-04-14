# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Segment'
        db.create_table(u'motifdiscovery_segment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['motifdiscovery.File'])),
            ('rounded_start', self.gf('django.db.models.fields.FloatField')()),
            ('rounded_end', self.gf('django.db.models.fields.FloatField')()),
            ('segment_path', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal(u'motifdiscovery', ['Segment'])

        # Adding field 'Pattern.segment'
        db.add_column(u'motifdiscovery_pattern', 'segment',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='patterns', null=True, to=orm['motifdiscovery.Segment']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Segment'
        db.delete_table(u'motifdiscovery_segment')

        # Deleting field 'Pattern.segment'
        db.delete_column(u'motifdiscovery_pattern', 'segment_id')


    models = {
        u'motifdiscovery.file': {
            'Meta': {'object_name': 'File'},
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'hasseed': ('django.db.models.fields.BooleanField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'})
        },
        u'motifdiscovery.match': {
            'Meta': {'object_name': 'Match'},
            'distance': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'match_sources'", 'to': u"orm['motifdiscovery.Pattern']"}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'match_targets'", 'to': u"orm['motifdiscovery.Pattern']"}),
            'version': ('django.db.models.fields.IntegerField', [], {})
        },
        u'motifdiscovery.pattern': {
            'Meta': {'object_name': 'Pattern'},
            'end_time': ('django.db.models.fields.FloatField', [], {}),
            'file': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['motifdiscovery.File']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isseed': ('django.db.models.fields.BooleanField', [], {}),
            'pair_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'segment': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'patterns'", 'null': 'True', 'to': u"orm['motifdiscovery.Segment']"}),
            'start_time': ('django.db.models.fields.FloatField', [], {})
        },
        u'motifdiscovery.segment': {
            'Meta': {'object_name': 'Segment'},
            'file': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['motifdiscovery.File']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rounded_end': ('django.db.models.fields.FloatField', [], {}),
            'rounded_start': ('django.db.models.fields.FloatField', [], {}),
            'segment_path': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        }
    }

    complete_apps = ['motifdiscovery']