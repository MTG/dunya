# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Label'
        db.delete_table(u'data_label')

        # Removing M2M table for field references on 'Label'
        db.delete_table(db.shorten_name(u'data_label_references'))

        # Removing M2M table for field images on 'Label'
        db.delete_table(db.shorten_name(u'data_label_images'))


    def backwards(self, orm):
        # Adding model 'Label'
        db.create_table(u'data_label', (
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.Description'], null=True, blank=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(related_name='label_source_set', null=True, to=orm['data.Source'], blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'data', ['Label'])

        # Adding M2M table for field references on 'Label'
        m2m_table_name = db.shorten_name(u'data_label_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('label', models.ForeignKey(orm[u'data.label'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['label_id', 'source_id'])

        # Adding M2M table for field images on 'Label'
        m2m_table_name = db.shorten_name(u'data_label_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('label', models.ForeignKey(orm[u'data.label'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['label_id', 'image_id'])


    models = {
        u'data.description': {
            'Meta': {'object_name': 'Description'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Source']", 'null': 'True', 'blank': 'True'})
        },
        u'data.image': {
            'Meta': {'object_name': 'Image'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'small_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Source']", 'null': 'True', 'blank': 'True'})
        },
        u'data.source': {
            'Meta': {'object_name': 'Source'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'source_name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.SourceName']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'data.sourcename': {
            'Meta': {'object_name': 'SourceName'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'data.visitlog': {
            'Meta': {'object_name': 'VisitLog'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['data']