# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CollectionLogMessage'
        db.create_table(u'dashboard_collectionlogmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.Collection'])),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'dashboard', ['CollectionLogMessage'])


        # Changing field 'ReleaseLogMessage.checker'
        db.alter_column(u'dashboard_releaselogmessage', 'checker_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.CompletenessChecker'], null=True))

    def backwards(self, orm):
        # Deleting model 'CollectionLogMessage'
        db.delete_table(u'dashboard_collectionlogmessage')


        # User chose to not deal with backwards NULL issues for 'ReleaseLogMessage.checker'
        raise RuntimeError("Cannot reverse this migration. 'ReleaseLogMessage.checker' and its values cannot be restored.")

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
            'checker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.CompletenessChecker']", 'null': 'True', 'blank': 'True'}),
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