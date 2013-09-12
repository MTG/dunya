# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'FileLogMessage'
        db.delete_table(u'dashboard_filelogmessage')

        # Deleting model 'ReleaseStatus'
        db.delete_table(u'dashboard_releasestatus')

        # Deleting model 'FileStatus'
        db.delete_table(u'dashboard_filestatus')

        # Deleting model 'Test'
        db.delete_table(u'dashboard_test')

        # Adding model 'CollectionFileLogMessage'
        db.create_table(u'dashboard_collectionfilelogmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collectionfile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CollectionFile'])),
            ('checker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CompletenessChecker'])),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'dashboard', ['CollectionFileLogMessage'])

        # Adding model 'MusicbrainzReleaseResult'
        db.create_table(u'dashboard_musicbrainzreleaseresult', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('musicbrainzrelease', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.MusicbrainzRelease'], null=True, blank=True)),
            ('checker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CompletenessChecker'])),
            ('result', self.gf('django.db.models.fields.CharField')(default='n', max_length=10)),
            ('data', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'dashboard', ['MusicbrainzReleaseResult'])

        # Adding model 'CollectionFileResult'
        db.create_table(u'dashboard_collectionfileresult', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('collectionfile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CollectionFile'], null=True, blank=True)),
            ('checker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CompletenessChecker'])),
            ('result', self.gf('django.db.models.fields.CharField')(default='n', max_length=10)),
            ('data', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'dashboard', ['CollectionFileResult'])


    def backwards(self, orm):
        # Adding model 'FileLogMessage'
        db.create_table(u'dashboard_filelogmessage', (
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CollectionFile'])),
            ('checker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CompletenessChecker'])),
            ('message', self.gf('django.db.models.fields.TextField')()),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'dashboard', ['FileLogMessage'])

        # Adding model 'ReleaseStatus'
        db.create_table(u'dashboard_releasestatus', (
            ('status', self.gf('django.db.models.fields.CharField')(default='n', max_length=10)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('checker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CompletenessChecker'])),
            ('release', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.MusicbrainzRelease'], null=True, blank=True)),
            ('data', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'dashboard', ['ReleaseStatus'])

        # Adding model 'FileStatus'
        db.create_table(u'dashboard_filestatus', (
            ('status', self.gf('django.db.models.fields.CharField')(default='n', max_length=10)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('checker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CompletenessChecker'])),
            ('file', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CollectionFile'], null=True, blank=True)),
            ('data', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'dashboard', ['FileStatus'])

        # Adding model 'Test'
        db.create_table(u'dashboard_test', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'dashboard', ['Test'])

        # Deleting model 'CollectionFileLogMessage'
        db.delete_table(u'dashboard_collectionfilelogmessage')

        # Deleting model 'MusicbrainzReleaseResult'
        db.delete_table(u'dashboard_musicbrainzreleaseresult')

        # Deleting model 'CollectionFileResult'
        db.delete_table(u'dashboard_collectionfileresult')


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
        u'dashboard.collectionfilelogmessage': {
            'Meta': {'object_name': 'CollectionFileLogMessage'},
            'checker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CompletenessChecker']"}),
            'collectionfile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CollectionFile']"}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {})
        },
        u'dashboard.collectionfileresult': {
            'Meta': {'object_name': 'CollectionFileResult'},
            'checker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CompletenessChecker']"}),
            'collectionfile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CollectionFile']", 'null': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'result': ('django.db.models.fields.CharField', [], {'default': "'n'", 'max_length': '10'})
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
        u'dashboard.musicbrainzrelease': {
            'Meta': {'unique_together': "(('mbid', 'collection'),)", 'object_name': 'MusicbrainzRelease'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.Collection']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'dashboard.musicbrainzreleaselogmessage': {
            'Meta': {'object_name': 'MusicbrainzReleaseLogMessage'},
            'checker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CompletenessChecker']", 'null': 'True', 'blank': 'True'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'musicbrainzrelease': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.MusicbrainzRelease']"})
        },
        u'dashboard.musicbrainzreleaseresult': {
            'Meta': {'object_name': 'MusicbrainzReleaseResult'},
            'checker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CompletenessChecker']"}),
            'data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'musicbrainzrelease': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.MusicbrainzRelease']", 'null': 'True', 'blank': 'True'}),
            'result': ('django.db.models.fields.CharField', [], {'default': "'n'", 'max_length': '10'})
        },
        u'dashboard.musicbrainzreleasestate': {
            'Meta': {'object_name': 'MusicbrainzReleaseState'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'musicbrainzrelease': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.MusicbrainzRelease']"}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'n'", 'max_length': '10'}),
            'state_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        }
    }

    complete_apps = ['dashboard']