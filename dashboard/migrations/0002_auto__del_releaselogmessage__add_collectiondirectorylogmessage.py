# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'ReleaseLogMessage'
        db.delete_table(u'dashboard_releaselogmessage')

        # Adding model 'CollectionDirectoryLogMessage'
        db.create_table(u'dashboard_collectiondirectorylogmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collectiondirectory', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CollectionDirectory'])),
            ('checker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CompletenessChecker'], null=True, blank=True)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'dashboard', ['CollectionDirectoryLogMessage'])


    def backwards(self, orm):
        # Adding model 'ReleaseLogMessage'
        db.create_table(u'dashboard_releaselogmessage', (
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('checker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CompletenessChecker'], null=True, blank=True)),
            ('release', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CollectionDirectory'])),
            ('message', self.gf('django.db.models.fields.TextField')()),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'dashboard', ['ReleaseLogMessage'])

        # Deleting model 'CollectionDirectoryLogMessage'
        db.delete_table(u'dashboard_collectiondirectorylogmessage')


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
            'Meta': {'object_name': 'CollectionDirectoryLogMessage'},
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'dashboard.collectionfilestate': {
            'Meta': {'object_name': 'CollectionFileState'},
            'collectionfile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CollectionFile']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'n'", 'max_length': '10'}),
            'state_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        u'dashboard.collectionlogmessage': {
            'Meta': {'object_name': 'CollectionLogMessage'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.Collection']"}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {})
        },
        u'dashboard.collectionstate': {
            'Meta': {'object_name': 'CollectionState'},
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
            'type': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        },
        u'dashboard.filelogmessage': {
            'Meta': {'object_name': 'FileLogMessage'},
            'checker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CompletenessChecker']"}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CollectionFile']"})
        },
        u'dashboard.filestatus': {
            'Meta': {'object_name': 'FileStatus'},
            'checker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CompletenessChecker']"}),
            'data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'file': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CollectionFile']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'n'", 'max_length': '10'})
        },
        u'dashboard.musicbrainzrelease': {
            'Meta': {'unique_together': "(('mbid', 'collection'),)", 'object_name': 'MusicbrainzRelease'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.Collection']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'dashboard.musicbrainzreleasestate': {
            'Meta': {'object_name': 'MusicbrainzReleaseState'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'musicbrainzrelease': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.MusicbrainzRelease']"}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'n'", 'max_length': '10'}),
            'state_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        u'dashboard.releasestatus': {
            'Meta': {'object_name': 'ReleaseStatus'},
            'checker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CompletenessChecker']"}),
            'data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'release': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.MusicbrainzRelease']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'n'", 'max_length': '10'})
        },
        u'dashboard.test': {
            'Meta': {'object_name': 'Test'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['dashboard']