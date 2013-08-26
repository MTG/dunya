# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Document.external_identifier'
        db.add_column(u'docserver_document', 'external_identifier',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'File.external_identifier'
        db.delete_column(u'docserver_file', 'external_identifier')


    def backwards(self, orm):
        # Deleting field 'Document.external_identifier'
        db.delete_column(u'docserver_document', 'external_identifier')


        # User chose to not deal with backwards NULL issues for 'File.external_identifier'
        raise RuntimeError("Cannot reverse this migration. 'File.external_identifier' and its values cannot be restored.")

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
            'docid': ('django.db.models.fields.CharField', [], {'default': "'9d4cf0ea-d721-413a-93da-763832c58ab6'", 'max_length': '36', 'primary_key': 'True'}),
            'external_identifier': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'docserver.essentiaversion': {
            'Meta': {'object_name': 'EssentiaVersion'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sha1': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'docserver.file': {
            'Meta': {'object_name': 'File'},
            'document': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'files'", 'to': u"orm['docserver.Document']"}),
            'file_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.FileType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'docserver.filetype': {
            'Meta': {'object_name': 'FileType'},
            'derived_from': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.FileType']", 'null': 'True', 'blank': 'True'}),
            'extension': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_derived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'docserver.module': {
            'Meta': {'object_name': 'Module'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'docserver.moduleversion': {
            'Meta': {'object_name': 'ModuleVersion'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.Module']"}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'docserver.runresult': {
            'Meta': {'object_name': 'RunResult'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'essentiaversion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.EssentiaVersion']"}),
            'file': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.File']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moduleversion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.ModuleVersion']"}),
            'workermachine': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.WorkerMachine']"})
        },
        u'docserver.workermachine': {
            'Meta': {'object_name': 'WorkerMachine'},
            'essentiaversions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['docserver.EssentiaVersion']", 'through': u"orm['docserver.WorkerMachineEssentiaVersion']", 'symmetrical': 'False'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moduleversions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['docserver.ModuleVersion']", 'through': u"orm['docserver.WorkerMachineModuleVersion']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'docserver.workermachineessentiaversion': {
            'Meta': {'object_name': 'WorkerMachineEssentiaVersion'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'essentiaversion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.EssentiaVersion']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'workermachine': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.WorkerMachine']"})
        },
        u'docserver.workermachinemoduleversion': {
            'Meta': {'object_name': 'WorkerMachineModuleVersion'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moduleversion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.ModuleVersion']"}),
            'workermachine': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.WorkerMachine']"})
        }
    }

    complete_apps = ['docserver']