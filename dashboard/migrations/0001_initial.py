# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CompletenessChecker'
        db.create_table(u'dashboard_completenesschecker', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('module', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=5)),
        ))
        db.send_create_signal(u'dashboard', ['CompletenessChecker'])

        # Adding model 'CollectionState'
        db.create_table(u'dashboard_collectionstate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.Collection'])),
            ('state', self.gf('django.db.models.fields.CharField')(default='n', max_length=10)),
            ('state_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'dashboard', ['CollectionState'])

        # Adding model 'Test'
        db.create_table(u'dashboard_test', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'dashboard', ['Test'])

        # Adding model 'Collection'
        db.create_table(u'dashboard_collection', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('root_directory', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'dashboard', ['Collection'])

        # Adding model 'CollectionLogMessage'
        db.create_table(u'dashboard_collectionlogmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.Collection'])),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'dashboard', ['CollectionLogMessage'])

        # Adding model 'MusicbrainzReleaseState'
        db.create_table(u'dashboard_musicbrainzreleasestate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('musicbrainzrelease', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.MusicbrainzRelease'])),
            ('state', self.gf('django.db.models.fields.CharField')(default='n', max_length=10)),
            ('state_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'dashboard', ['MusicbrainzReleaseState'])

        # Adding model 'MusicbrainzRelease'
        db.create_table(u'dashboard_musicbrainzrelease', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, blank=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.Collection'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'dashboard', ['MusicbrainzRelease'])

        # Adding unique constraint on 'MusicbrainzRelease', fields ['mbid', 'collection']
        db.create_unique(u'dashboard_musicbrainzrelease', ['mbid', 'collection_id'])

        # Adding model 'CollectionDirectory'
        db.create_table(u'dashboard_collectiondirectory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.Collection'])),
            ('musicbrainzrelease', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.MusicbrainzRelease'], null=True, blank=True)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'dashboard', ['CollectionDirectory'])

        # Adding model 'ReleaseLogMessage'
        db.create_table(u'dashboard_releaselogmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('release', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CollectionDirectory'])),
            ('checker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CompletenessChecker'], null=True, blank=True)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'dashboard', ['ReleaseLogMessage'])

        # Adding model 'CollectionFileState'
        db.create_table(u'dashboard_collectionfilestate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collectionfile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CollectionFile'])),
            ('state', self.gf('django.db.models.fields.CharField')(default='n', max_length=10)),
            ('state_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'dashboard', ['CollectionFileState'])

        # Adding model 'CollectionFile'
        db.create_table(u'dashboard_collectionfile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('directory', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CollectionDirectory'])),
        ))
        db.send_create_signal(u'dashboard', ['CollectionFile'])

        # Adding model 'FileLogMessage'
        db.create_table(u'dashboard_filelogmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CollectionFile'])),
            ('checker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CompletenessChecker'])),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'dashboard', ['FileLogMessage'])

        # Adding model 'FileStatus'
        db.create_table(u'dashboard_filestatus', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('file', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CollectionFile'], null=True, blank=True)),
            ('checker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CompletenessChecker'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='n', max_length=10)),
            ('data', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'dashboard', ['FileStatus'])

        # Adding model 'ReleaseStatus'
        db.create_table(u'dashboard_releasestatus', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('release', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.MusicbrainzRelease'], null=True, blank=True)),
            ('checker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CompletenessChecker'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='n', max_length=10)),
            ('data', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'dashboard', ['ReleaseStatus'])


    def backwards(self, orm):
        # Removing unique constraint on 'MusicbrainzRelease', fields ['mbid', 'collection']
        db.delete_unique(u'dashboard_musicbrainzrelease', ['mbid', 'collection_id'])

        # Deleting model 'CompletenessChecker'
        db.delete_table(u'dashboard_completenesschecker')

        # Deleting model 'CollectionState'
        db.delete_table(u'dashboard_collectionstate')

        # Deleting model 'Test'
        db.delete_table(u'dashboard_test')

        # Deleting model 'Collection'
        db.delete_table(u'dashboard_collection')

        # Deleting model 'CollectionLogMessage'
        db.delete_table(u'dashboard_collectionlogmessage')

        # Deleting model 'MusicbrainzReleaseState'
        db.delete_table(u'dashboard_musicbrainzreleasestate')

        # Deleting model 'MusicbrainzRelease'
        db.delete_table(u'dashboard_musicbrainzrelease')

        # Deleting model 'CollectionDirectory'
        db.delete_table(u'dashboard_collectiondirectory')

        # Deleting model 'ReleaseLogMessage'
        db.delete_table(u'dashboard_releaselogmessage')

        # Deleting model 'CollectionFileState'
        db.delete_table(u'dashboard_collectionfilestate')

        # Deleting model 'CollectionFile'
        db.delete_table(u'dashboard_collectionfile')

        # Deleting model 'FileLogMessage'
        db.delete_table(u'dashboard_filelogmessage')

        # Deleting model 'FileStatus'
        db.delete_table(u'dashboard_filestatus')

        # Deleting model 'ReleaseStatus'
        db.delete_table(u'dashboard_releasestatus')


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
        u'dashboard.releaselogmessage': {
            'Meta': {'object_name': 'ReleaseLogMessage'},
            'checker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CompletenessChecker']", 'null': 'True', 'blank': 'True'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'release': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CollectionDirectory']"})
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