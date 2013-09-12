# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Collection'
        db.create_table(u'docserver_collection', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('root_dir', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'docserver', ['Collection'])

        # Adding model 'Document'
        db.create_table(u'docserver_document', (
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(related_name='documents', to=orm['docserver.Collection'])),
            ('docid', self.gf('django.db.models.fields.CharField')(default='77afa123-f461-4418-8add-d9b278ad284a', max_length=36, primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'docserver', ['Document'])

        # Adding model 'FileType'
        db.create_table(u'docserver_filetype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('extension', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('is_derived', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('derived_from', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['docserver.FileType'])),
        ))
        db.send_create_signal(u'docserver', ['FileType'])

        # Adding model 'File'
        db.create_table(u'docserver_file', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(related_name='files', to=orm['docserver.Document'])),
            ('file_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['docserver.FileType'])),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('external_identifier', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('disambiguation', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal(u'docserver', ['File'])

        # Adding model 'FileConverter'
        db.create_table(u'docserver_fileconverter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('to_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['docserver.FileType'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('conversion_class', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'docserver', ['FileConverter'])


    def backwards(self, orm):
        # Deleting model 'Collection'
        db.delete_table(u'docserver_collection')

        # Deleting model 'Document'
        db.delete_table(u'docserver_document')

        # Deleting model 'FileType'
        db.delete_table(u'docserver_filetype')

        # Deleting model 'File'
        db.delete_table(u'docserver_file')

        # Deleting model 'FileConverter'
        db.delete_table(u'docserver_fileconverter')


    models = {
        u'docserver.collection': {
            'Meta': {'object_name': 'Collection'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'root_dir': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        u'docserver.document': {
            'Meta': {'object_name': 'Document'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'documents'", 'to': u"orm['docserver.Collection']"}),
            'docid': ('django.db.models.fields.CharField', [], {'default': "'5da26ed5-8ef8-4187-a00f-e58c4b18feb6'", 'max_length': '36', 'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'docserver.file': {
            'Meta': {'object_name': 'File'},
            'disambiguation': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'document': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'files'", 'to': u"orm['docserver.Document']"}),
            'external_identifier': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'file_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.FileType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'docserver.fileconverter': {
            'Meta': {'object_name': 'FileConverter'},
            'conversion_class': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.FileType']"})
        },
        u'docserver.filetype': {
            'Meta': {'object_name': 'FileType'},
            'derived_from': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.FileType']"}),
            'extension': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_derived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['docserver']