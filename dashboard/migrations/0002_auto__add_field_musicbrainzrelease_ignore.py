# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'MusicbrainzRelease.ignore'
        db.add_column(u'dashboard_musicbrainzrelease', 'ignore',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'MusicbrainzRelease.ignore'
        db.delete_column(u'dashboard_musicbrainzrelease', 'ignore')


    models = {
        u'dashboard.collection': {
            'Meta': {'object_name': 'Collection'},
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'root_directory': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'dashboard.collectiondirectory': {
            'Meta': {'object_name': 'CollectionDirectory'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.Collection']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'musicbrainzrelease': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.MusicbrainzRelease']", 'null': 'True', 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'dashboard.collectiondirectorylogmessage': {
            'Meta': {'ordering': "['-datetime']", 'object_name': 'CollectionDirectoryLogMessage'},
            'checker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CompletenessChecker']", 'null': 'True', 'blank': 'True'}),
            'collectiondirectory': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CollectionDirectory']"}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {})
        },
        u'dashboard.collectionfile': {
            'Meta': {'object_name': 'CollectionFile'},
            'directory': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CollectionDirectory']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'recordingid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'})
        },
        u'dashboard.collectionfilelogmessage': {
            'Meta': {'ordering': "['-datetime']", 'object_name': 'CollectionFileLogMessage'},
            'checker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CompletenessChecker']"}),
            'collectionfile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CollectionFile']"}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {})
        },
        u'dashboard.collectionfileresult': {
            'Meta': {'ordering': "['-datetime']", 'object_name': 'CollectionFileResult'},
            'checker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CompletenessChecker']"}),
            'collectionfile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CollectionFile']"}),
            'data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'dashboard.collectionfilestate': {
            'Meta': {'ordering': "['-state_date']", 'object_name': 'CollectionFileState'},
            'collectionfile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CollectionFile']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'n'", 'max_length': '10'}),
            'state_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        u'dashboard.collectionlogmessage': {
            'Meta': {'ordering': "['-datetime']", 'object_name': 'CollectionLogMessage'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.Collection']"}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {})
        },
        u'dashboard.collectionstate': {
            'Meta': {'ordering': "['-state_date']", 'object_name': 'CollectionState'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.Collection']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'n'", 'max_length': '10'}),
            'state_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        u'dashboard.completenesschecker': {
            'Meta': {'object_name': 'CompletenessChecker'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'templatefile': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        },
        u'dashboard.musicbrainzrelease': {
            'Meta': {'unique_together': "(('mbid', 'collection'),)", 'object_name': 'MusicbrainzRelease'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.Collection']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ignore': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'dashboard.musicbrainzreleaselogmessage': {
            'Meta': {'ordering': "['-datetime']", 'object_name': 'MusicbrainzReleaseLogMessage'},
            'checker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CompletenessChecker']", 'null': 'True', 'blank': 'True'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'musicbrainzrelease': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.MusicbrainzRelease']"})
        },
        u'dashboard.musicbrainzreleaseresult': {
            'Meta': {'ordering': "['-datetime']", 'object_name': 'MusicbrainzReleaseResult'},
            'checker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CompletenessChecker']"}),
            'data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'musicbrainzrelease': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.MusicbrainzRelease']", 'null': 'True', 'blank': 'True'}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'dashboard.musicbrainzreleasestate': {
            'Meta': {'ordering': "['-state_date']", 'object_name': 'MusicbrainzReleaseState'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'musicbrainzrelease': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.MusicbrainzRelease']"}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'n'", 'max_length': '10'}),
            'state_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        }
    }

    complete_apps = ['dashboard']