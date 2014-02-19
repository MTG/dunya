# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Instrument'
        db.create_table(u'hindustani_instrument', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'hindustani_instrument_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('percussion', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'hindustani', ['Instrument'])

        # Adding M2M table for field references on 'Instrument'
        m2m_table_name = db.shorten_name(u'hindustani_instrument_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('instrument', models.ForeignKey(orm[u'hindustani.instrument'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['instrument_id', 'source_id'])

        # Adding M2M table for field images on 'Instrument'
        m2m_table_name = db.shorten_name(u'hindustani_instrument_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('instrument', models.ForeignKey(orm[u'hindustani.instrument'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['instrument_id', 'image_id'])

        # Adding model 'Artist'
        db.create_table(u'hindustani_artist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'hindustani_artist_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('begin', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('end', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('artist_type', self.gf('django.db.models.fields.CharField')(default='P', max_length=1)),
            ('main_instrument', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hindustani.Instrument'], null=True, blank=True)),
            ('dummy', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'hindustani', ['Artist'])

        # Adding M2M table for field references on 'Artist'
        m2m_table_name = db.shorten_name(u'hindustani_artist_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('artist', models.ForeignKey(orm[u'hindustani.artist'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['artist_id', 'source_id'])

        # Adding M2M table for field images on 'Artist'
        m2m_table_name = db.shorten_name(u'hindustani_artist_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('artist', models.ForeignKey(orm[u'hindustani.artist'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['artist_id', 'image_id'])

        # Adding M2M table for field group_members on 'Artist'
        m2m_table_name = db.shorten_name(u'hindustani_artist_group_members')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_artist', models.ForeignKey(orm[u'hindustani.artist'], null=False)),
            ('to_artist', models.ForeignKey(orm[u'hindustani.artist'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_artist_id', 'to_artist_id'])

        # Adding model 'Release'
        db.create_table(u'hindustani_release', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'hindustani_release_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('artistcredit', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('year', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'hindustani', ['Release'])

        # Adding M2M table for field references on 'Release'
        m2m_table_name = db.shorten_name(u'hindustani_release_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('release', models.ForeignKey(orm[u'hindustani.release'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['release_id', 'source_id'])

        # Adding M2M table for field images on 'Release'
        m2m_table_name = db.shorten_name(u'hindustani_release_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('release', models.ForeignKey(orm[u'hindustani.release'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['release_id', 'image_id'])

        # Adding M2M table for field artists on 'Release'
        m2m_table_name = db.shorten_name(u'hindustani_release_artists')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('release', models.ForeignKey(orm[u'hindustani.release'], null=False)),
            ('artist', models.ForeignKey(orm[u'hindustani.artist'], null=False))
        ))
        db.create_unique(m2m_table_name, ['release_id', 'artist_id'])

        # Adding model 'RecordingRaag'
        db.create_table(u'hindustani_recordingraag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hindustani.Recording'])),
            ('raag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hindustani.Raag'])),
            ('sequence', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'hindustani', ['RecordingRaag'])

        # Adding model 'RecordingTaal'
        db.create_table(u'hindustani_recordingtaal', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hindustani.Recording'])),
            ('taal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hindustani.Taal'])),
            ('laay', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hindustani.Laay'])),
            ('sequence', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'hindustani', ['RecordingTaal'])

        # Adding model 'RecordingSection'
        db.create_table(u'hindustani_recordingsection', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hindustani.Recording'])),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hindustani.Section'])),
            ('sequence', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'hindustani', ['RecordingSection'])

        # Adding model 'RecordingForm'
        db.create_table(u'hindustani_recordingform', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hindustani.Recording'])),
            ('form', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hindustani.Form'])),
            ('sequence', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'hindustani', ['RecordingForm'])

        # Adding model 'Recording'
        db.create_table(u'hindustani_recording', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'hindustani_recording_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('length', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'hindustani', ['Recording'])

        # Adding M2M table for field references on 'Recording'
        m2m_table_name = db.shorten_name(u'hindustani_recording_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('recording', models.ForeignKey(orm[u'hindustani.recording'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['recording_id', 'source_id'])

        # Adding M2M table for field images on 'Recording'
        m2m_table_name = db.shorten_name(u'hindustani_recording_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('recording', models.ForeignKey(orm[u'hindustani.recording'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['recording_id', 'image_id'])

        # Adding model 'InstrumentPerformance'
        db.create_table(u'hindustani_instrumentperformance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hindustani.Recording'])),
            ('performer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hindustani.Artist'])),
            ('instrument', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hindustani.Instrument'])),
            ('lead', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'hindustani', ['InstrumentPerformance'])

        # Adding model 'Composer'
        db.create_table(u'hindustani_composer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'hindustani_composer_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('begin', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('end', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
        ))
        db.send_create_signal(u'hindustani', ['Composer'])

        # Adding M2M table for field references on 'Composer'
        m2m_table_name = db.shorten_name(u'hindustani_composer_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('composer', models.ForeignKey(orm[u'hindustani.composer'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['composer_id', 'source_id'])

        # Adding M2M table for field images on 'Composer'
        m2m_table_name = db.shorten_name(u'hindustani_composer_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('composer', models.ForeignKey(orm[u'hindustani.composer'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['composer_id', 'image_id'])

        # Adding model 'Lyrics'
        db.create_table(u'hindustani_lyrics', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('lyrics', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'hindustani', ['Lyrics'])

        # Adding model 'Work'
        db.create_table(u'hindustani_work', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('lyrics', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hindustani.Lyrics'])),
        ))
        db.send_create_signal(u'hindustani', ['Work'])

        # Adding model 'Section'
        db.create_table(u'hindustani_section', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('transliteration', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'hindustani', ['Section'])

        # Adding model 'Raag'
        db.create_table(u'hindustani_raag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('transliteration', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'hindustani', ['Raag'])

        # Adding model 'RaagAlias'
        db.create_table(u'hindustani_raagalias', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('raag', self.gf('django.db.models.fields.related.ForeignKey')(related_name='aliases', to=orm['hindustani.Raag'])),
        ))
        db.send_create_signal(u'hindustani', ['RaagAlias'])

        # Adding model 'Taal'
        db.create_table(u'hindustani_taal', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('transliteration', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'hindustani', ['Taal'])

        # Adding model 'TaalAlias'
        db.create_table(u'hindustani_taalalias', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('taal', self.gf('django.db.models.fields.related.ForeignKey')(related_name='aliases', to=orm['hindustani.Taal'])),
        ))
        db.send_create_signal(u'hindustani', ['TaalAlias'])

        # Adding model 'Laay'
        db.create_table(u'hindustani_laay', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('transliteration', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'hindustani', ['Laay'])

        # Adding model 'LaayAlias'
        db.create_table(u'hindustani_laayalias', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('laay', self.gf('django.db.models.fields.related.ForeignKey')(related_name='aliases', to=orm['hindustani.Laay'])),
        ))
        db.send_create_signal(u'hindustani', ['LaayAlias'])

        # Adding model 'Form'
        db.create_table(u'hindustani_form', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('transliteration', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'hindustani', ['Form'])

        # Adding model 'FormAlias'
        db.create_table(u'hindustani_formalias', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('form', self.gf('django.db.models.fields.related.ForeignKey')(related_name='aliases', to=orm['hindustani.Form'])),
        ))
        db.send_create_signal(u'hindustani', ['FormAlias'])


    def backwards(self, orm):
        # Deleting model 'Instrument'
        db.delete_table(u'hindustani_instrument')

        # Removing M2M table for field references on 'Instrument'
        db.delete_table(db.shorten_name(u'hindustani_instrument_references'))

        # Removing M2M table for field images on 'Instrument'
        db.delete_table(db.shorten_name(u'hindustani_instrument_images'))

        # Deleting model 'Artist'
        db.delete_table(u'hindustani_artist')

        # Removing M2M table for field references on 'Artist'
        db.delete_table(db.shorten_name(u'hindustani_artist_references'))

        # Removing M2M table for field images on 'Artist'
        db.delete_table(db.shorten_name(u'hindustani_artist_images'))

        # Removing M2M table for field group_members on 'Artist'
        db.delete_table(db.shorten_name(u'hindustani_artist_group_members'))

        # Deleting model 'Release'
        db.delete_table(u'hindustani_release')

        # Removing M2M table for field references on 'Release'
        db.delete_table(db.shorten_name(u'hindustani_release_references'))

        # Removing M2M table for field images on 'Release'
        db.delete_table(db.shorten_name(u'hindustani_release_images'))

        # Removing M2M table for field artists on 'Release'
        db.delete_table(db.shorten_name(u'hindustani_release_artists'))

        # Deleting model 'RecordingRaag'
        db.delete_table(u'hindustani_recordingraag')

        # Deleting model 'RecordingTaal'
        db.delete_table(u'hindustani_recordingtaal')

        # Deleting model 'RecordingSection'
        db.delete_table(u'hindustani_recordingsection')

        # Deleting model 'RecordingForm'
        db.delete_table(u'hindustani_recordingform')

        # Deleting model 'Recording'
        db.delete_table(u'hindustani_recording')

        # Removing M2M table for field references on 'Recording'
        db.delete_table(db.shorten_name(u'hindustani_recording_references'))

        # Removing M2M table for field images on 'Recording'
        db.delete_table(db.shorten_name(u'hindustani_recording_images'))

        # Deleting model 'InstrumentPerformance'
        db.delete_table(u'hindustani_instrumentperformance')

        # Deleting model 'Composer'
        db.delete_table(u'hindustani_composer')

        # Removing M2M table for field references on 'Composer'
        db.delete_table(db.shorten_name(u'hindustani_composer_references'))

        # Removing M2M table for field images on 'Composer'
        db.delete_table(db.shorten_name(u'hindustani_composer_images'))

        # Deleting model 'Lyrics'
        db.delete_table(u'hindustani_lyrics')

        # Deleting model 'Work'
        db.delete_table(u'hindustani_work')

        # Deleting model 'Section'
        db.delete_table(u'hindustani_section')

        # Deleting model 'Raag'
        db.delete_table(u'hindustani_raag')

        # Deleting model 'RaagAlias'
        db.delete_table(u'hindustani_raagalias')

        # Deleting model 'Taal'
        db.delete_table(u'hindustani_taal')

        # Deleting model 'TaalAlias'
        db.delete_table(u'hindustani_taalalias')

        # Deleting model 'Laay'
        db.delete_table(u'hindustani_laay')

        # Deleting model 'LaayAlias'
        db.delete_table(u'hindustani_laayalias')

        # Deleting model 'Form'
        db.delete_table(u'hindustani_form')

        # Deleting model 'FormAlias'
        db.delete_table(u'hindustani_formalias')


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
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lyrics': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hindustani.Lyrics']"})
        }
    }

    complete_apps = ['hindustani']