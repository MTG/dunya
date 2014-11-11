# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Module.disabled'
        db.add_column(u'docserver_module', 'disabled',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Module.disabled'
        db.delete_column(u'docserver_module', 'disabled')


    models = {
        u'docserver.collection': {
            'Meta': {'object_name': 'Collection'},
            'collectionid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'root_directory': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        u'docserver.derivedfile': {
            'Meta': {'object_name': 'DerivedFile'},
            'computation_time': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'derived_from': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.SourceFile']"}),
            'document': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'derivedfiles'", 'to': u"orm['docserver.Document']"}),
            'essentia': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.EssentiaVersion']", 'null': 'True', 'blank': 'True'}),
            'extension': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'module_version': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.ModuleVersion']"}),
            'outputname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'pycompmusic': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.PyCompmusicVersion']", 'null': 'True', 'blank': 'True'})
        },
        u'docserver.derivedfilepart': {
            'Meta': {'object_name': 'DerivedFilePart'},
            'derivedfile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parts'", 'to': u"orm['docserver.DerivedFile']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'part_order': ('django.db.models.fields.IntegerField', [], {}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'size': ('django.db.models.fields.IntegerField', [], {})
        },
        u'docserver.document': {
            'Meta': {'object_name': 'Document'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'documents'", 'to': u"orm['docserver.Collection']"}),
            'external_identifier': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'docserver.documentlogmessage': {
            'Meta': {'ordering': "['-datetime']", 'object_name': 'DocumentLogMessage'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'document': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'logs'", 'to': u"orm['docserver.Document']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'moduleversion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.ModuleVersion']", 'null': 'True', 'blank': 'True'}),
            'sourcefile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.SourceFile']", 'null': 'True', 'blank': 'True'})
        },
        u'docserver.essentiaversion': {
            'Meta': {'object_name': 'EssentiaVersion'},
            'commit_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sha1': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'docserver.module': {
            'Meta': {'object_name': 'Module'},
            'collections': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['docserver.Collection']", 'symmetrical': 'False'}),
            'depends': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'disabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'source_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.SourceFileType']"})
        },
        u'docserver.moduleversion': {
            'Meta': {'object_name': 'ModuleVersion'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'versions'", 'to': u"orm['docserver.Module']"}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'docserver.pycompmusicversion': {
            'Meta': {'object_name': 'PyCompmusicVersion'},
            'commit_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sha1': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'docserver.sourcefile': {
            'Meta': {'object_name': 'SourceFile'},
            'document': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sourcefiles'", 'to': u"orm['docserver.Document']"}),
            'file_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.SourceFileType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'size': ('django.db.models.fields.IntegerField', [], {})
        },
        u'docserver.sourcefiletype': {
            'Meta': {'object_name': 'SourceFileType'},
            'extension': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'docserver.worker': {
            'Meta': {'object_name': 'Worker'},
            'essentia': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.EssentiaVersion']", 'null': 'True', 'blank': 'True'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pycompmusic': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.PyCompmusicVersion']", 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'})
        }
    }

    complete_apps = ['docserver']