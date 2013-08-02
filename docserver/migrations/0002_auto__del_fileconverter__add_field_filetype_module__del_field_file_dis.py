# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'FileConverter'
        db.delete_table(u'docserver_fileconverter')

        # Adding field 'FileType.module'
        db.add_column(u'docserver_filetype', 'module',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255),
                      keep_default=False)

        # Deleting field 'File.disambiguation'
        db.delete_column(u'docserver_file', 'disambiguation')


    def backwards(self, orm):
        # Adding model 'FileConverter'
        db.create_table(u'docserver_fileconverter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('to_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['docserver.FileType'])),
            ('conversion_class', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'docserver', ['FileConverter'])

        # Deleting field 'FileType.module'
        db.delete_column(u'docserver_filetype', 'module')


        # User chose to not deal with backwards NULL issues for 'File.disambiguation'
        raise RuntimeError("Cannot reverse this migration. 'File.disambiguation' and its values cannot be restored.")

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
            'docid': ('django.db.models.fields.CharField', [], {'default': "'c223c4fb-5ff5-403b-a301-78fd8b4f4673'", 'max_length': '36', 'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'docserver.file': {
            'Meta': {'object_name': 'File'},
            'document': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'files'", 'to': u"orm['docserver.Document']"}),
            'external_identifier': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'file_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.FileType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'docserver.filetype': {
            'Meta': {'object_name': 'FileType'},
            'derived_from': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.FileType']"}),
            'extension': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_derived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['docserver']