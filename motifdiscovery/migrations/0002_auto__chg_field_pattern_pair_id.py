# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Pattern.pair_id'
        db.alter_column(u'motifdiscovery_pattern', 'pair_id', self.gf('django.db.models.fields.IntegerField')(null=True))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Pattern.pair_id'
        raise RuntimeError("Cannot reverse this migration. 'Pattern.pair_id' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Pattern.pair_id'
        db.alter_column(u'motifdiscovery_pattern', 'pair_id', self.gf('django.db.models.fields.IntegerField')())

    models = {
        u'motifdiscovery.file': {
            'Meta': {'object_name': 'File'},
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'hasseed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'isseed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pair_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.FloatField', [], {})
        }
    }

    complete_apps = ['motifdiscovery']