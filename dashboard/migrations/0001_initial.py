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
            ('templatefile', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
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

        # Adding model 'MusicbrainzReleaseLogMessage'
        db.create_table(u'dashboard_musicbrainzreleaselogmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('musicbrainzrelease', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.MusicbrainzRelease'])),
            ('checker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CompletenessChecker'], null=True, blank=True)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'dashboard', ['MusicbrainzReleaseLogMessage'])

        # Adding model 'CollectionDirectory'
        db.create_table(u'dashboard_collectiondirectory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.Collection'])),
            ('musicbrainzrelease', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.MusicbrainzRelease'], null=True, blank=True)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'dashboard', ['CollectionDirectory'])

        # Adding model 'CollectionDirectoryLogMessage'
        db.create_table(u'dashboard_collectiondirectorylogmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collectiondirectory', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CollectionDirectory'])),
            ('checker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CompletenessChecker'], null=True, blank=True)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'dashboard', ['CollectionDirectoryLogMessage'])

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
            ('recordingid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
        ))
        db.send_create_signal(u'dashboard', ['CollectionFile'])

        # Adding model 'CollectionFileLogMessage'
        db.create_table(u'dashboard_collectionfilelogmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collectionfile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CollectionFile'])),
            ('checker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CompletenessChecker'])),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'dashboard', ['CollectionFileLogMessage'])

        # Adding model 'CollectionFileResult'
        db.create_table(u'dashboard_collectionfileresult', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('collectionfile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CollectionFile'])),
            ('checker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CompletenessChecker'])),
            ('result', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('data', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'dashboard', ['CollectionFileResult'])

        # Adding model 'MusicbrainzReleaseResult'
        db.create_table(u'dashboard_musicbrainzreleaseresult', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('musicbrainzrelease', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.MusicbrainzRelease'], null=True, blank=True)),
            ('checker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CompletenessChecker'])),
            ('result', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('data', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'dashboard', ['MusicbrainzReleaseResult'])


    def backwards(self, orm):
        # Removing unique constraint on 'MusicbrainzRelease', fields ['mbid', 'collection']
        db.delete_unique(u'dashboard_musicbrainzrelease', ['mbid', 'collection_id'])

        # Deleting model 'CompletenessChecker'
        db.delete_table(u'dashboard_completenesschecker')

        # Deleting model 'CollectionState'
        db.delete_table(u'dashboard_collectionstate')

        # Deleting model 'Collection'
        db.delete_table(u'dashboard_collection')

        # Deleting model 'CollectionLogMessage'
        db.delete_table(u'dashboard_collectionlogmessage')

        # Deleting model 'MusicbrainzReleaseState'
        db.delete_table(u'dashboard_musicbrainzreleasestate')

        # Deleting model 'MusicbrainzRelease'
        db.delete_table(u'dashboard_musicbrainzrelease')

        # Deleting model 'MusicbrainzReleaseLogMessage'
        db.delete_table(u'dashboard_musicbrainzreleaselogmessage')

        # Deleting model 'CollectionDirectory'
        db.delete_table(u'dashboard_collectiondirectory')

        # Deleting model 'CollectionDirectoryLogMessage'
        db.delete_table(u'dashboard_collectiondirectorylogmessage')

        # Deleting model 'CollectionFileState'
        db.delete_table(u'dashboard_collectionfilestate')

        # Deleting model 'CollectionFile'
        db.delete_table(u'dashboard_collectionfile')

        # Deleting model 'CollectionFileLogMessage'
        db.delete_table(u'dashboard_collectionfilelogmessage')

        # Deleting model 'CollectionFileResult'
        db.delete_table(u'dashboard_collectionfileresult')

        # Deleting model 'MusicbrainzReleaseResult'
        db.delete_table(u'dashboard_musicbrainzreleaseresult')


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