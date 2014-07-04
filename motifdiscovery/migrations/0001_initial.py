# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'File'
        db.create_table(u'motifdiscovery_file', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('hasseed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'motifdiscovery', ['File'])

        # Adding model 'Match'
        db.create_table(u'motifdiscovery_match', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(related_name='match_sources', to=orm['motifdiscovery.Pattern'])),
            ('target', self.gf('django.db.models.fields.related.ForeignKey')(related_name='match_targets', to=orm['motifdiscovery.Pattern'])),
            ('distance', self.gf('django.db.models.fields.FloatField')()),
            ('version', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'motifdiscovery', ['Match'])

        # Adding model 'Pattern'
        db.create_table(u'motifdiscovery_pattern', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['motifdiscovery.File'])),
            ('start_time', self.gf('django.db.models.fields.FloatField')()),
            ('end_time', self.gf('django.db.models.fields.FloatField')()),
            ('pair_id', self.gf('django.db.models.fields.IntegerField')()),
            ('isseed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'motifdiscovery', ['Pattern'])


    def backwards(self, orm):
        # Deleting model 'File'
        db.delete_table(u'motifdiscovery_file')

        # Deleting model 'Match'
        db.delete_table(u'motifdiscovery_match')

        # Deleting model 'Pattern'
        db.delete_table(u'motifdiscovery_pattern')


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
            'pair_id': ('django.db.models.fields.IntegerField', [], {}),
            'start_time': ('django.db.models.fields.FloatField', [], {})
        }
    }

    complete_apps = ['motifdiscovery']