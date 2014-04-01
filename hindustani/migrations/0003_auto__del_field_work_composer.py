# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Work.composer'
        db.delete_column(u'hindustani_work', 'composer_id')

        # Adding M2M table for field composers on 'Work'
        m2m_table_name = db.shorten_name(u'hindustani_work_composers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('work', models.ForeignKey(orm[u'hindustani.work'], null=False)),
            ('composer', models.ForeignKey(orm[u'hindustani.composer'], null=False))
        ))
        db.create_unique(m2m_table_name, ['work_id', 'composer_id'])

        # Adding M2M table for field lyricists on 'Work'
        m2m_table_name = db.shorten_name(u'hindustani_work_lyricists')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('work', models.ForeignKey(orm[u'hindustani.work'], null=False)),
            ('composer', models.ForeignKey(orm[u'hindustani.composer'], null=False))
        ))
        db.create_unique(m2m_table_name, ['work_id', 'composer_id'])


    def backwards(self, orm):
        # Adding field 'Work.composer'
        db.add_column(u'hindustani_work', 'composer',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hindustani.Composer'], null=True, blank=True),
                      keep_default=False)

        # Removing M2M table for field composers on 'Work'
        db.delete_table(db.shorten_name(u'hindustani_work_composers'))

        # Removing M2M table for field lyricists on 'Work'
        db.delete_table(db.shorten_name(u'hindustani_work_lyricists'))


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
        u'hindustani.form': {
            'Meta': {'object_name': 'Form'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'transliteration': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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
        u'hindustani.laay': {
            'Meta': {'object_name': 'Laay'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'transliteration': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'hindustani.laayalias': {
            'Meta': {'object_name': 'LaayAlias'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'laay': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'to': u"orm['hindustani.Laay']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'hindustani.lyrics': {
            'Meta': {'object_name': 'Lyrics'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lyrics': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'hindustani.raag': {
            'Meta': {'object_name': 'Raag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'transliteration': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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
            'length': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'performance': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['hindustani.Artist']", 'through': u"orm['hindustani.InstrumentPerformance']", 'symmetrical': 'False'}),
            'raags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['hindustani.Raag']", 'through': u"orm['hindustani.RecordingRaag']", 'symmetrical': 'False'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'hindustani_recording_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'sections': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['hindustani.Section']", 'through': u"orm['hindustani.RecordingSection']", 'symmetrical': 'False'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'hindustani_recording_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'taals': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['hindustani.Taal']", 'through': u"orm['hindustani.RecordingTaal']", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'works': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['hindustani.Work']", 'through': u"orm['hindustani.WorkTime']", 'symmetrical': 'False'})
        },
        u'hindustani.recordingform': {
            'Meta': {'object_name': 'RecordingForm'},
            'form': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hindustani.Form']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'laay': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hindustani.Laay']"}),
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
            'year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'hindustani.section': {
            'Meta': {'object_name': 'Section'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'transliteration': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'hindustani.taal': {
            'Meta': {'object_name': 'Taal'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'transliteration': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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
            'lyrics': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hindustani.Lyrics']"}),
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