# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Collection'
        db.create_table(u'docserver_collection', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collectionid', self.gf('django.db.models.fields.CharField')(max_length=36, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('root_directory', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'docserver', ['Collection'])

        # Adding model 'Document'
        db.create_table(u'docserver_document', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(related_name='documents', to=orm['docserver.Collection'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('external_identifier', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'docserver', ['Document'])

        # Adding model 'SourceFileType'
        db.create_table(u'docserver_sourcefiletype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('extension', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'docserver', ['SourceFileType'])

        # Adding model 'SourceFile'
        db.create_table(u'docserver_sourcefile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sourcefiles', to=orm['docserver.Document'])),
            ('file_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['docserver.SourceFileType'])),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('size', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'docserver', ['SourceFile'])

        # Adding model 'DerivedFilePart'
        db.create_table(u'docserver_derivedfilepart', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('derivedfile', self.gf('django.db.models.fields.related.ForeignKey')(related_name='parts', to=orm['docserver.DerivedFile'])),
            ('part_order', self.gf('django.db.models.fields.IntegerField')()),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('size', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'docserver', ['DerivedFilePart'])

        # Adding model 'DerivedFile'
        db.create_table(u'docserver_derivedfile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(related_name='derivedfiles', to=orm['docserver.Document'])),
            ('derived_from', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['docserver.SourceFile'])),
            ('module_version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['docserver.ModuleVersion'])),
            ('outputname', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('extension', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('mimetype', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('computation_time', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'docserver', ['DerivedFile'])

        # Adding model 'EssentiaVersion'
        db.create_table(u'docserver_essentiaversion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('sha1', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'docserver', ['EssentiaVersion'])

        # Adding model 'Module'
        db.create_table(u'docserver_module', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('depends', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('module', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('source_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['docserver.SourceFileType'])),
        ))
        db.send_create_signal(u'docserver', ['Module'])

        # Adding M2M table for field collections on 'Module'
        m2m_table_name = db.shorten_name(u'docserver_module_collections')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('module', models.ForeignKey(orm[u'docserver.module'], null=False)),
            ('collection', models.ForeignKey(orm[u'docserver.collection'], null=False))
        ))
        db.create_unique(m2m_table_name, ['module_id', 'collection_id'])

        # Adding model 'ModuleVersion'
        db.create_table(u'docserver_moduleversion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('module', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['docserver.Module'])),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'docserver', ['ModuleVersion'])

        # Adding model 'DocumentLogMessage'
        db.create_table(u'docserver_documentlogmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(related_name='logs', to=orm['docserver.Document'])),
            ('moduleversion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['docserver.ModuleVersion'], null=True, blank=True)),
            ('sourcefile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['docserver.SourceFile'], null=True, blank=True)),
            ('level', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'docserver', ['DocumentLogMessage'])


    def backwards(self, orm):
        # Deleting model 'Collection'
        db.delete_table(u'docserver_collection')

        # Deleting model 'Document'
        db.delete_table(u'docserver_document')

        # Deleting model 'SourceFileType'
        db.delete_table(u'docserver_sourcefiletype')

        # Deleting model 'SourceFile'
        db.delete_table(u'docserver_sourcefile')

        # Deleting model 'DerivedFilePart'
        db.delete_table(u'docserver_derivedfilepart')

        # Deleting model 'DerivedFile'
        db.delete_table(u'docserver_derivedfile')

        # Deleting model 'EssentiaVersion'
        db.delete_table(u'docserver_essentiaversion')

        # Deleting model 'Module'
        db.delete_table(u'docserver_module')

        # Removing M2M table for field collections on 'Module'
        db.delete_table(db.shorten_name(u'docserver_module_collections'))

        # Deleting model 'ModuleVersion'
        db.delete_table(u'docserver_moduleversion')

        # Deleting model 'DocumentLogMessage'
        db.delete_table(u'docserver_documentlogmessage')


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
            'extension': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'module_version': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.ModuleVersion']"}),
            'outputname': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sha1': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'docserver.module': {
            'Meta': {'object_name': 'Module'},
            'collections': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['docserver.Collection']", 'symmetrical': 'False'}),
            'depends': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
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
            'module': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['docserver.Module']"}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '10'})
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
        }
    }

    complete_apps = ['docserver']