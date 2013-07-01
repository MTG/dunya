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

        # Adding model 'Collection'
        db.create_table(u'dashboard_collection', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('root_directory', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'dashboard', ['Collection'])

        # Adding model 'CollectionState'
        db.create_table(u'dashboard_collectionstate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.Collection'])),
            ('state', self.gf('django.db.models.fields.CharField')(default='n', max_length=10)),
            ('state_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'dashboard', ['CollectionState'])

        # Adding model 'MusicbrainzRelease'
        db.create_table(u'dashboard_musicbrainzrelease', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.Collection'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'dashboard', ['MusicbrainzRelease'])

        # Adding model 'CollectionDirectory'
        db.create_table(u'dashboard_collectiondirectory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.Collection'])),
            ('musicbrainz_release', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.MusicbrainzRelease'], null=True, blank=True)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'dashboard', ['CollectionDirectory'])

        # Adding model 'ReleaseState'
        db.create_table(u'dashboard_releasestate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('release', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CollectionDirectory'])),
            ('state', self.gf('django.db.models.fields.CharField')(default='n', max_length=10)),
            ('state_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'dashboard', ['ReleaseState'])

        # Adding model 'ReleaseLogMessage'
        db.create_table(u'dashboard_releaselogmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('release', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CollectionDirectory'])),
            ('checker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CompletenessChecker'])),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'dashboard', ['ReleaseLogMessage'])

        # Adding model 'CollectionFile'
        db.create_table(u'dashboard_collectionfile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('directory', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CollectionDirectory'])),
        ))
        db.send_create_signal(u'dashboard', ['CollectionFile'])

        # Adding model 'FileState'
        db.create_table(u'dashboard_filestate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CollectionFile'])),
            ('state', self.gf('django.db.models.fields.CharField')(default='n', max_length=10)),
            ('state_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'dashboard', ['FileState'])

        # Adding model 'FileLogMessage'
        db.create_table(u'dashboard_filelogmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CollectionFile'])),
            ('checker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CompletenessChecker'])),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'dashboard', ['FileLogMessage'])

        # Adding model 'Status'
        db.create_table(u'dashboard_status', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CollectionFile'])),
            ('monitor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CompletenessChecker'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='s', max_length=10)),
        ))
        db.send_create_signal(u'dashboard', ['Status'])


    def backwards(self, orm):
        # Deleting model 'CompletenessChecker'
        db.delete_table(u'dashboard_completenesschecker')

        # Deleting model 'Collection'
        db.delete_table(u'dashboard_collection')

        # Deleting model 'CollectionState'
        db.delete_table(u'dashboard_collectionstate')

        # Deleting model 'MusicbrainzRelease'
        db.delete_table(u'dashboard_musicbrainzrelease')

        # Deleting model 'CollectionDirectory'
        db.delete_table(u'dashboard_collectiondirectory')

        # Deleting model 'ReleaseState'
        db.delete_table(u'dashboard_releasestate')

        # Deleting model 'ReleaseLogMessage'
        db.delete_table(u'dashboard_releaselogmessage')

        # Deleting model 'CollectionFile'
        db.delete_table(u'dashboard_collectionfile')

        # Deleting model 'FileState'
        db.delete_table(u'dashboard_filestate')

        # Deleting model 'FileLogMessage'
        db.delete_table(u'dashboard_filelogmessage')

        # Deleting model 'Status'
        db.delete_table(u'dashboard_status')


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
            'musicbrainz_release': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.MusicbrainzRelease']", 'null': 'True', 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'dashboard.collectionfile': {
            'Meta': {'object_name': 'CollectionFile'},
            'directory': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CollectionDirectory']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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
        u'dashboard.filestate': {
            'Meta': {'object_name': 'FileState'},
            'file': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CollectionFile']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'n'", 'max_length': '10'}),
            'state_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        u'dashboard.musicbrainzrelease': {
            'Meta': {'object_name': 'MusicbrainzRelease'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.Collection']"}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'dashboard.releaselogmessage': {
            'Meta': {'object_name': 'ReleaseLogMessage'},
            'checker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CompletenessChecker']"}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'release': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CollectionDirectory']"})
        },
        u'dashboard.releasestate': {
            'Meta': {'object_name': 'ReleaseState'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'release': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CollectionDirectory']"}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'n'", 'max_length': '10'}),
            'state_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        u'dashboard.status': {
            'Meta': {'object_name': 'Status'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monitor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CompletenessChecker']"}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CollectionFile']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'s'", 'max_length': '10'})
        }
    }

    complete_apps = ['dashboard']