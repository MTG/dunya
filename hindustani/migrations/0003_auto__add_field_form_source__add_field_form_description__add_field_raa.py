# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Form.source'
        db.add_column(u'hindustani_form', 'source',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'hindustani_form_source_set', null=True, to=orm['data.Source']),
                      keep_default=False)

        # Adding field 'Form.description'
        db.add_column(u'hindustani_form', 'description',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description']),
                      keep_default=False)

        # Adding M2M table for field references on 'Form'
        m2m_table_name = db.shorten_name(u'hindustani_form_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('form', models.ForeignKey(orm[u'hindustani.form'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['form_id', 'source_id'])

        # Adding M2M table for field images on 'Form'
        m2m_table_name = db.shorten_name(u'hindustani_form_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('form', models.ForeignKey(orm[u'hindustani.form'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['form_id', 'image_id'])

        # Adding field 'Raag.source'
        db.add_column(u'hindustani_raag', 'source',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'hindustani_raag_source_set', null=True, to=orm['data.Source']),
                      keep_default=False)

        # Adding field 'Raag.description'
        db.add_column(u'hindustani_raag', 'description',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description']),
                      keep_default=False)

        # Adding M2M table for field references on 'Raag'
        m2m_table_name = db.shorten_name(u'hindustani_raag_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('raag', models.ForeignKey(orm[u'hindustani.raag'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['raag_id', 'source_id'])

        # Adding M2M table for field images on 'Raag'
        m2m_table_name = db.shorten_name(u'hindustani_raag_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('raag', models.ForeignKey(orm[u'hindustani.raag'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['raag_id', 'image_id'])

        # Adding field 'Laya.source'
        db.add_column(u'hindustani_laya', 'source',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'hindustani_laya_source_set', null=True, to=orm['data.Source']),
                      keep_default=False)

        # Adding field 'Laya.description'
        db.add_column(u'hindustani_laya', 'description',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description']),
                      keep_default=False)

        # Adding M2M table for field references on 'Laya'
        m2m_table_name = db.shorten_name(u'hindustani_laya_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('laya', models.ForeignKey(orm[u'hindustani.laya'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['laya_id', 'source_id'])

        # Adding M2M table for field images on 'Laya'
        m2m_table_name = db.shorten_name(u'hindustani_laya_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('laya', models.ForeignKey(orm[u'hindustani.laya'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['laya_id', 'image_id'])

        # Adding field 'Taal.source'
        db.add_column(u'hindustani_taal', 'source',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'hindustani_taal_source_set', null=True, to=orm['data.Source']),
                      keep_default=False)

        # Adding field 'Taal.description'
        db.add_column(u'hindustani_taal', 'description',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description']),
                      keep_default=False)

        # Adding M2M table for field references on 'Taal'
        m2m_table_name = db.shorten_name(u'hindustani_taal_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('taal', models.ForeignKey(orm[u'hindustani.taal'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['taal_id', 'source_id'])

        # Adding M2M table for field images on 'Taal'
        m2m_table_name = db.shorten_name(u'hindustani_taal_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('taal', models.ForeignKey(orm[u'hindustani.taal'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['taal_id', 'image_id'])


    def backwards(self, orm):
        # Deleting field 'Form.source'
        db.delete_column(u'hindustani_form', 'source_id')

        # Deleting field 'Form.description'
        db.delete_column(u'hindustani_form', 'description_id')

        # Removing M2M table for field references on 'Form'
        db.delete_table(db.shorten_name(u'hindustani_form_references'))

        # Removing M2M table for field images on 'Form'
        db.delete_table(db.shorten_name(u'hindustani_form_images'))

        # Deleting field 'Raag.source'
        db.delete_column(u'hindustani_raag', 'source_id')

        # Deleting field 'Raag.description'
        db.delete_column(u'hindustani_raag', 'description_id')

        # Removing M2M table for field references on 'Raag'
        db.delete_table(db.shorten_name(u'hindustani_raag_references'))

        # Removing M2M table for field images on 'Raag'
        db.delete_table(db.shorten_name(u'hindustani_raag_images'))

        # Deleting field 'Laya.source'
        db.delete_column(u'hindustani_laya', 'source_id')

        # Deleting field 'Laya.description'
        db.delete_column(u'hindustani_laya', 'description_id')

        # Removing M2M table for field references on 'Laya'
        db.delete_table(db.shorten_name(u'hindustani_laya_references'))

        # Removing M2M table for field images on 'Laya'
        db.delete_table(db.shorten_name(u'hindustani_laya_images'))

        # Deleting field 'Taal.source'
        db.delete_column(u'hindustani_taal', 'source_id')

        # Deleting field 'Taal.description'
        db.delete_column(u'hindustani_taal', 'description_id')

        # Removing M2M table for field references on 'Taal'
        db.delete_table(db.shorten_name(u'hindustani_taal_references'))

        # Removing M2M table for field images on 'Taal'
        db.delete_table(db.shorten_name(u'hindustani_taal_images'))


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
        u'hindustani.artist': {
            'Meta': {'object_name': 'Artist'},
            'artist_type': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '1'}),
            'begin': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            'dummy': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'group_members': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'groups'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['hindustani.Artist']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'hindustani_artist_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'main_instrument': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hindustani.Instrument']", 'null': 'True', 'blank': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'hindustani_artist_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'hindustani_artist_source_set'", 'null': 'True', 'to': u"orm['data.Source']"})
        },
        u'hindustani.artistalias': {
            'Meta': {'object_name': 'ArtistAlias'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'to': u"orm['hindustani.Artist']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locale': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'hindustani.composer': {
            'Meta': {'object_name': 'Composer'},
            'begin': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            'end': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'hindustani_composer_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'hindustani_composer_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'hindustani_composer_source_set'", 'null': 'True', 'to': u"orm['data.Source']"})
        },
        u'hindustani.composeralias': {
            'Meta': {'object_name': 'ComposerAlias'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'composer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'to': u"orm['hindustani.Composer']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locale': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'hindustani.form': {
            'Meta': {'object_name': 'Form'},
            'common_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'hindustani_form_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'hindustani_form_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'hindustani_form_source_set'", 'null': 'True', 'to': u"orm['data.Source']"})
        },
        u'hindustani.formalias': {
            'Meta': {'object_name': 'FormAlias'},
            'form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'to': u"orm['hindustani.Form']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'hindustani.instrument': {
            'Meta': {'object_name': 'Instrument'},
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'hindustani_instrument_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'percussion': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'hindustani_instrument_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'hindustani_instrument_source_set'", 'null': 'True', 'to': u"orm['data.Source']"})
        },
        u'hindustani.instrumentperformance': {
            'Meta': {'object_name': 'InstrumentPerformance'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instrument': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hindustani.Instrument']"}),
            'lead': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'performer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hindustani.Artist']"}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hindustani.Recording']"})
        },
        u'hindustani.laya': {
            'Meta': {'object_name': 'Laya'},
            'common_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'hindustani_laya_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'hindustani_laya_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'hindustani_laya_source_set'", 'null': 'True', 'to': u"orm['data.Source']"})
        },
        u'hindustani.layaalias': {
            'Meta': {'object_name': 'LayaAlias'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'laya': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'to': u"orm['hindustani.Laya']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'hindustani.lyrics': {
            'Meta': {'object_name': 'Lyrics'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lyrics': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'hindustani.raag': {
            'Meta': {'object_name': 'Raag'},
            'common_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'hindustani_raag_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'hindustani_raag_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'hindustani_raag_source_set'", 'null': 'True', 'to': u"orm['data.Source']"})
        },
        u'hindustani.raagalias': {
            'Meta': {'object_name': 'RaagAlias'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'raag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'to': u"orm['hindustani.Raag']"})
        },
        u'hindustani.recording': {
            'Meta': {'object_name': 'Recording'},
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            'forms': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['hindustani.Form']", 'through': u"orm['hindustani.RecordingForm']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'hindustani_recording_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'layas': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['hindustani.Laya']", 'through': u"orm['hindustani.RecordingLaya']", 'symmetrical': 'False'}),
            'length': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'performance': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['hindustani.Artist']", 'through': u"orm['hindustani.InstrumentPerformance']", 'symmetrical': 'False'}),
            'raags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['hindustani.Raag']", 'through': u"orm['hindustani.RecordingRaag']", 'symmetrical': 'False'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'hindustani_recording_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'sections': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['hindustani.Section']", 'through': u"orm['hindustani.RecordingSection']", 'symmetrical': 'False'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'hindustani_recording_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'taals': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['hindustani.Taal']", 'through': u"orm['hindustani.RecordingTaal']", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'works': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['hindustani.Work']", 'through': u"orm['hindustani.WorkTime']", 'symmetrical': 'False'})
        },
        u'hindustani.recordingform': {
            'Meta': {'object_name': 'RecordingForm'},
            'form': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hindustani.Form']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hindustani.Recording']"}),
            'sequence': ('django.db.models.fields.IntegerField', [], {})
        },
        u'hindustani.recordinglaya': {
            'Meta': {'object_name': 'RecordingLaya'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'laya': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hindustani.Laya']"}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hindustani.Recording']"}),
            'sequence': ('django.db.models.fields.IntegerField', [], {})
        },
        u'hindustani.recordingraag': {
            'Meta': {'object_name': 'RecordingRaag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'raag': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hindustani.Raag']"}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hindustani.Recording']"}),
            'sequence': ('django.db.models.fields.IntegerField', [], {})
        },
        u'hindustani.recordingsection': {
            'Meta': {'object_name': 'RecordingSection'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hindustani.Recording']"}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hindustani.Section']"}),
            'sequence': ('django.db.models.fields.IntegerField', [], {})
        },
        u'hindustani.recordingtaal': {
            'Meta': {'object_name': 'RecordingTaal'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hindustani.Recording']"}),
            'sequence': ('django.db.models.fields.IntegerField', [], {}),
            'taal': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hindustani.Taal']"})
        },
        u'hindustani.release': {
            'Meta': {'object_name': 'Release'},
            'artistcredit': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'artists': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'primary_concerts'", 'symmetrical': 'False', 'to': u"orm['hindustani.Artist']"}),
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'hindustani_release_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'hindustani_release_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'hindustani_release_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tracks': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['hindustani.Recording']", 'through': u"orm['hindustani.ReleaseRecording']", 'symmetrical': 'False'}),
            'year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'hindustani.releaserecording': {
            'Meta': {'object_name': 'ReleaseRecording'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hindustani.Recording']"}),
            'release': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hindustani.Release']"}),
            'track': ('django.db.models.fields.IntegerField', [], {})
        },
        u'hindustani.section': {
            'Meta': {'object_name': 'Section'},
            'common_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'hindustani.sectionalias': {
            'Meta': {'object_name': 'SectionAlias'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'to': u"orm['hindustani.Section']"})
        },
        u'hindustani.taal': {
            'Meta': {'object_name': 'Taal'},
            'common_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'hindustani_taal_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'hindustani_taal_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'hindustani_taal_source_set'", 'null': 'True', 'to': u"orm['data.Source']"})
        },
        u'hindustani.taalalias': {
            'Meta': {'object_name': 'TaalAlias'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'taal': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'to': u"orm['hindustani.Taal']"})
        },
        u'hindustani.work': {
            'Meta': {'object_name': 'Work'},
            'composers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'works'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['hindustani.Composer']"}),
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'hindustani_work_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'lyricists': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'lyric_works'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['hindustani.Composer']"}),
            'lyrics': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hindustani.Lyrics']", 'null': 'True', 'blank': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'hindustani_work_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'hindustani_work_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'hindustani.worktime': {
            'Meta': {'object_name': 'WorkTime'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hindustani.Recording']"}),
            'sequence': ('django.db.models.fields.IntegerField', [], {}),
            'time': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hindustani.Work']"})
        }
    }

    complete_apps = ['hindustani']