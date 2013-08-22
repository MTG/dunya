# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'RunResult'
        db.create_table(u'docserver_runresult', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('essentiaversion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['docserver.EssentiaVersion'])),
            ('file', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['docserver.File'])),
            ('workermachine', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['docserver.WorkerMachine'])),
            ('moduleversion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['docserver.ModuleVersion'])),
        ))
        db.send_create_signal(u'docserver', ['RunResult'])

        # Adding model 'WorkerMachine'
        db.create_table(u'docserver_workermachine', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')(max_length=200)),
            ('hostname', self.gf('django.db.models.fields.TextField')(max_length=200)),
        ))
        db.send_create_signal(u'docserver', ['WorkerMachine'])

        # Adding model 'WorkerMachineEssentiaVersion'
        db.create_table(u'docserver_workermachineessentiaversion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('essentiaversion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['docserver.EssentiaVersion'])),
            ('workermachine', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['docserver.WorkerMachine'])),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'docserver', ['WorkerMachineEssentiaVersion'])

        # Adding model 'Module'
        db.create_table(u'docserver_module', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')(max_length=200)),
            ('path', self.gf('django.db.models.fields.TextField')(max_length=200)),
        ))
        db.send_create_signal(u'docserver', ['Module'])

        # Adding model 'ModuleVersion'
        db.create_table(u'docserver_moduleversion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('module', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['docserver.Module'])),
            ('version', self.gf('django.db.models.fields.TextField')(max_length=10)),
        ))
        db.send_create_signal(u'docserver', ['ModuleVersion'])

        # Adding model 'WorkerMachineModuleVersion'
        db.create_table(u'docserver_workermachinemoduleversion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('workermachine', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['docserver.WorkerMachine'])),
            ('moduleversion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['docserver.ModuleVersion'])),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'docserver', ['WorkerMachineModuleVersion'])

        # Adding model 'EssentiaVersion'
        db.create_table(u'docserver_essentiaversion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('version', self.gf('django.db.models.fields.TextField')(max_length=200)),
            ('sha1', self.gf('django.db.models.fields.TextField')(max_length=200)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'docserver', ['EssentiaVersion'])


    def backwards(self, orm):
        # Deleting model 'RunResult'
        db.delete_table(u'docserver_runresult')

        # Deleting model 'WorkerMachine'
        db.delete_table(u'docserver_workermachine')

        # Deleting model 'WorkerMachineEssentiaVersion'
        db.delete_table(u'docserver_workermachineessentiaversion')

        # Deleting model 'Module'
        db.delete_table(u'docserver_module')

        # Deleting model 'ModuleVersion'
        db.delete_table(u'docserver_moduleversion')

        # Deleting model 'WorkerMachineModuleVersion'
        db.delete_table(u'docserver_workermachinemoduleversion')

        # Deleting model 'EssentiaVersion'
        db.delete_table(u'docserver_essentiaversion')


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
            'docid': ('django.db.models.fields.CharField', [], {'default': "'d773628c-c131-420f-a34a-5c061651c112'", 'max_length': '36', 'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'docserver.essentiaversion': {
            'Meta': {'object_name': 'EssentiaVersion'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sha1': ('django.db.models.fields.TextField', [], {'max_length': '200'}),
            'version': ('django.db.models.fields.TextField', [], {'max_length': '200'})
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
            'name': ('django.db.models.fields.TextField', [], {'max_length': '200'}),
            'path': ('django.db.models.fields.TextField', [], {'max_length': '200'})
        },
        u'docserver.moduleversion': {
            'Meta': {'object_name': 'ModuleVersion'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.Module']"}),
            'version': ('django.db.models.fields.TextField', [], {'max_length': '10'})
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
            'hostname': ('django.db.models.fields.TextField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moduleversions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['docserver.ModuleVersion']", 'through': u"orm['docserver.WorkerMachineModuleVersion']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.TextField', [], {'max_length': '200'})
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