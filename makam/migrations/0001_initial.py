# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ArtistAlias'
        db.create_table(u'makam_artistalias', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(related_name='aliases', to=orm['makam.Artist'])),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('primary', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('locale', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
        ))
        db.send_create_signal(u'makam', ['ArtistAlias'])

        # Adding model 'Artist'
        db.create_table(u'makam_artist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'makam_artist_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('begin', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('end', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('artist_type', self.gf('django.db.models.fields.CharField')(default='P', max_length=1)),
            ('main_instrument', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['makam.Instrument'], null=True, blank=True)),
            ('dummy', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'makam', ['Artist'])

        # Adding M2M table for field references on 'Artist'
        m2m_table_name = db.shorten_name(u'makam_artist_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('artist', models.ForeignKey(orm[u'makam.artist'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['artist_id', 'source_id'])

        # Adding M2M table for field images on 'Artist'
        m2m_table_name = db.shorten_name(u'makam_artist_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('artist', models.ForeignKey(orm[u'makam.artist'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['artist_id', 'image_id'])

        # Adding M2M table for field group_members on 'Artist'
        m2m_table_name = db.shorten_name(u'makam_artist_group_members')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_artist', models.ForeignKey(orm[u'makam.artist'], null=False)),
            ('to_artist', models.ForeignKey(orm[u'makam.artist'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_artist_id', 'to_artist_id'])

        # Adding model 'ComposerAlias'
        db.create_table(u'makam_composeralias', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('composer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='aliases', to=orm['makam.Composer'])),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('primary', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('locale', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
        ))
        db.send_create_signal(u'makam', ['ComposerAlias'])

        # Adding model 'Composer'
        db.create_table(u'makam_composer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'makam_composer_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('begin', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('end', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
        ))
        db.send_create_signal(u'makam', ['Composer'])

        # Adding M2M table for field references on 'Composer'
        m2m_table_name = db.shorten_name(u'makam_composer_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('composer', models.ForeignKey(orm[u'makam.composer'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['composer_id', 'source_id'])

        # Adding M2M table for field images on 'Composer'
        m2m_table_name = db.shorten_name(u'makam_composer_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('composer', models.ForeignKey(orm[u'makam.composer'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['composer_id', 'image_id'])

        # Adding model 'Release'
        db.create_table(u'makam_release', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'makam_release_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('artistcredit', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('year', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('is_concert', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'makam', ['Release'])

        # Adding M2M table for field references on 'Release'
        m2m_table_name = db.shorten_name(u'makam_release_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('release', models.ForeignKey(orm[u'makam.release'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['release_id', 'source_id'])

        # Adding M2M table for field images on 'Release'
        m2m_table_name = db.shorten_name(u'makam_release_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('release', models.ForeignKey(orm[u'makam.release'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['release_id', 'image_id'])

        # Adding M2M table for field artists on 'Release'
        m2m_table_name = db.shorten_name(u'makam_release_artists')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('release', models.ForeignKey(orm[u'makam.release'], null=False)),
            ('artist', models.ForeignKey(orm[u'makam.artist'], null=False))
        ))
        db.create_unique(m2m_table_name, ['release_id', 'artist_id'])

        # Adding model 'ReleaseRecording'
        db.create_table(u'makam_releaserecording', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('release', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['makam.Release'])),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['makam.Recording'])),
            ('track', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'makam', ['ReleaseRecording'])

        # Adding model 'RecordingWork'
        db.create_table(u'makam_recordingwork', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('work', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['makam.Work'])),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['makam.Recording'])),
            ('sequence', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'makam', ['RecordingWork'])

        # Adding model 'Recording'
        db.create_table(u'makam_recording', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'makam_recording_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('length', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'makam', ['Recording'])

        # Adding M2M table for field references on 'Recording'
        m2m_table_name = db.shorten_name(u'makam_recording_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('recording', models.ForeignKey(orm[u'makam.recording'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['recording_id', 'source_id'])

        # Adding M2M table for field images on 'Recording'
        m2m_table_name = db.shorten_name(u'makam_recording_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('recording', models.ForeignKey(orm[u'makam.recording'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['recording_id', 'image_id'])

        # Adding model 'InstrumentPerformance'
        db.create_table(u'makam_instrumentperformance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['makam.Recording'])),
            ('performer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['makam.Artist'])),
            ('instrument', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['makam.Instrument'])),
            ('lead', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'makam', ['InstrumentPerformance'])

        # Adding model 'Instrument'
        db.create_table(u'makam_instrument', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'makam_instrument_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('percussion', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'makam', ['Instrument'])

        # Adding M2M table for field references on 'Instrument'
        m2m_table_name = db.shorten_name(u'makam_instrument_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('instrument', models.ForeignKey(orm[u'makam.instrument'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['instrument_id', 'source_id'])

        # Adding M2M table for field images on 'Instrument'
        m2m_table_name = db.shorten_name(u'makam_instrument_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('instrument', models.ForeignKey(orm[u'makam.instrument'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['instrument_id', 'image_id'])

        # Adding model 'MakamAlias'
        db.create_table(u'makam_makamalias', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('makam', self.gf('django.db.models.fields.related.ForeignKey')(related_name='aliases', to=orm['makam.Makam'])),
        ))
        db.send_create_signal(u'makam', ['MakamAlias'])

        # Adding model 'Makam'
        db.create_table(u'makam_makam', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'makam', ['Makam'])

        # Adding model 'UsulAlias'
        db.create_table(u'makam_usulalias', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('usul', self.gf('django.db.models.fields.related.ForeignKey')(related_name='aliases', to=orm['makam.Usul'])),
        ))
        db.send_create_signal(u'makam', ['UsulAlias'])

        # Adding model 'Usul'
        db.create_table(u'makam_usul', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'makam', ['Usul'])

        # Adding model 'FormAlias'
        db.create_table(u'makam_formalias', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('form', self.gf('django.db.models.fields.related.ForeignKey')(related_name='aliases', to=orm['makam.Form'])),
        ))
        db.send_create_signal(u'makam', ['FormAlias'])

        # Adding model 'Form'
        db.create_table(u'makam_form', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'makam', ['Form'])

        # Adding model 'Work'
        db.create_table(u'makam_work', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'makam_work_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('composition_date', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('is_taksim', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'makam', ['Work'])

        # Adding M2M table for field references on 'Work'
        m2m_table_name = db.shorten_name(u'makam_work_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('work', models.ForeignKey(orm[u'makam.work'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['work_id', 'source_id'])

        # Adding M2M table for field images on 'Work'
        m2m_table_name = db.shorten_name(u'makam_work_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('work', models.ForeignKey(orm[u'makam.work'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['work_id', 'image_id'])

        # Adding M2M table for field composers on 'Work'
        m2m_table_name = db.shorten_name(u'makam_work_composers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('work', models.ForeignKey(orm[u'makam.work'], null=False)),
            ('composer', models.ForeignKey(orm[u'makam.composer'], null=False))
        ))
        db.create_unique(m2m_table_name, ['work_id', 'composer_id'])

        # Adding M2M table for field lyricists on 'Work'
        m2m_table_name = db.shorten_name(u'makam_work_lyricists')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('work', models.ForeignKey(orm[u'makam.work'], null=False)),
            ('composer', models.ForeignKey(orm[u'makam.composer'], null=False))
        ))
        db.create_unique(m2m_table_name, ['work_id', 'composer_id'])

        # Adding M2M table for field makam on 'Work'
        m2m_table_name = db.shorten_name(u'makam_work_makam')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('work', models.ForeignKey(orm[u'makam.work'], null=False)),
            ('makam', models.ForeignKey(orm[u'makam.makam'], null=False))
        ))
        db.create_unique(m2m_table_name, ['work_id', 'makam_id'])

        # Adding M2M table for field usul on 'Work'
        m2m_table_name = db.shorten_name(u'makam_work_usul')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('work', models.ForeignKey(orm[u'makam.work'], null=False)),
            ('usul', models.ForeignKey(orm[u'makam.usul'], null=False))
        ))
        db.create_unique(m2m_table_name, ['work_id', 'usul_id'])

        # Adding M2M table for field form on 'Work'
        m2m_table_name = db.shorten_name(u'makam_work_form')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('work', models.ForeignKey(orm[u'makam.work'], null=False)),
            ('form', models.ForeignKey(orm[u'makam.form'], null=False))
        ))
        db.create_unique(m2m_table_name, ['work_id', 'form_id'])


    def backwards(self, orm):
        # Deleting model 'ArtistAlias'
        db.delete_table(u'makam_artistalias')

        # Deleting model 'Artist'
        db.delete_table(u'makam_artist')

        # Removing M2M table for field references on 'Artist'
        db.delete_table(db.shorten_name(u'makam_artist_references'))

        # Removing M2M table for field images on 'Artist'
        db.delete_table(db.shorten_name(u'makam_artist_images'))

        # Removing M2M table for field group_members on 'Artist'
        db.delete_table(db.shorten_name(u'makam_artist_group_members'))

        # Deleting model 'ComposerAlias'
        db.delete_table(u'makam_composeralias')

        # Deleting model 'Composer'
        db.delete_table(u'makam_composer')

        # Removing M2M table for field references on 'Composer'
        db.delete_table(db.shorten_name(u'makam_composer_references'))

        # Removing M2M table for field images on 'Composer'
        db.delete_table(db.shorten_name(u'makam_composer_images'))

        # Deleting model 'Release'
        db.delete_table(u'makam_release')

        # Removing M2M table for field references on 'Release'
        db.delete_table(db.shorten_name(u'makam_release_references'))

        # Removing M2M table for field images on 'Release'
        db.delete_table(db.shorten_name(u'makam_release_images'))

        # Removing M2M table for field artists on 'Release'
        db.delete_table(db.shorten_name(u'makam_release_artists'))

        # Deleting model 'ReleaseRecording'
        db.delete_table(u'makam_releaserecording')

        # Deleting model 'RecordingWork'
        db.delete_table(u'makam_recordingwork')

        # Deleting model 'Recording'
        db.delete_table(u'makam_recording')

        # Removing M2M table for field references on 'Recording'
        db.delete_table(db.shorten_name(u'makam_recording_references'))

        # Removing M2M table for field images on 'Recording'
        db.delete_table(db.shorten_name(u'makam_recording_images'))

        # Deleting model 'InstrumentPerformance'
        db.delete_table(u'makam_instrumentperformance')

        # Deleting model 'Instrument'
        db.delete_table(u'makam_instrument')

        # Removing M2M table for field references on 'Instrument'
        db.delete_table(db.shorten_name(u'makam_instrument_references'))

        # Removing M2M table for field images on 'Instrument'
        db.delete_table(db.shorten_name(u'makam_instrument_images'))

        # Deleting model 'MakamAlias'
        db.delete_table(u'makam_makamalias')

        # Deleting model 'Makam'
        db.delete_table(u'makam_makam')

        # Deleting model 'UsulAlias'
        db.delete_table(u'makam_usulalias')

        # Deleting model 'Usul'
        db.delete_table(u'makam_usul')

        # Deleting model 'FormAlias'
        db.delete_table(u'makam_formalias')

        # Deleting model 'Form'
        db.delete_table(u'makam_form')

        # Deleting model 'Work'
        db.delete_table(u'makam_work')

        # Removing M2M table for field references on 'Work'
        db.delete_table(db.shorten_name(u'makam_work_references'))

        # Removing M2M table for field images on 'Work'
        db.delete_table(db.shorten_name(u'makam_work_images'))

        # Removing M2M table for field composers on 'Work'
        db.delete_table(db.shorten_name(u'makam_work_composers'))

        # Removing M2M table for field lyricists on 'Work'
        db.delete_table(db.shorten_name(u'makam_work_lyricists'))

        # Removing M2M table for field makam on 'Work'
        db.delete_table(db.shorten_name(u'makam_work_makam'))

        # Removing M2M table for field usul on 'Work'
        db.delete_table(db.shorten_name(u'makam_work_usul'))

        # Removing M2M table for field form on 'Work'
        db.delete_table(db.shorten_name(u'makam_work_form'))


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
        u'makam.artist': {
            'Meta': {'object_name': 'Artist'},
            'artist_type': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '1'}),
            'begin': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            'dummy': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'group_members': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'groups'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['makam.Artist']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'makam_artist_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'main_instrument': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['makam.Instrument']", 'null': 'True', 'blank': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'makam_artist_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'makam_artist_source_set'", 'null': 'True', 'to': u"orm['data.Source']"})
        },
        u'makam.artistalias': {
            'Meta': {'object_name': 'ArtistAlias'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'to': u"orm['makam.Artist']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locale': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'makam.composer': {
            'Meta': {'object_name': 'Composer'},
            'begin': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            'end': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'makam_composer_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'makam_composer_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'makam_composer_source_set'", 'null': 'True', 'to': u"orm['data.Source']"})
        },
        u'makam.composeralias': {
            'Meta': {'object_name': 'ComposerAlias'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'composer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'to': u"orm['makam.Composer']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locale': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'makam.form': {
            'Meta': {'object_name': 'Form'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'makam.formalias': {
            'Meta': {'object_name': 'FormAlias'},
            'form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'to': u"orm['makam.Form']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'makam.instrument': {
            'Meta': {'object_name': 'Instrument'},
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'makam_instrument_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'percussion': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'makam_instrument_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'makam_instrument_source_set'", 'null': 'True', 'to': u"orm['data.Source']"})
        },
        u'makam.instrumentperformance': {
            'Meta': {'object_name': 'InstrumentPerformance'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instrument': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['makam.Instrument']"}),
            'lead': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'performer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['makam.Artist']"}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['makam.Recording']"})
        },
        u'makam.makam': {
            'Meta': {'object_name': 'Makam'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'makam.makamalias': {
            'Meta': {'object_name': 'MakamAlias'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'makam': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'to': u"orm['makam.Makam']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'makam.recording': {
            'Meta': {'object_name': 'Recording'},
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'makam_recording_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'length': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'performance': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['makam.Artist']", 'through': u"orm['makam.InstrumentPerformance']", 'symmetrical': 'False'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'makam_recording_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'makam_recording_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'works': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['makam.Work']", 'through': u"orm['makam.RecordingWork']", 'symmetrical': 'False'})
        },
        u'makam.recordingwork': {
            'Meta': {'object_name': 'RecordingWork'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['makam.Recording']"}),
            'sequence': ('django.db.models.fields.IntegerField', [], {}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['makam.Work']"})
        },
        u'makam.release': {
            'Meta': {'object_name': 'Release'},
            'artistcredit': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'artists': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'primary_concerts'", 'symmetrical': 'False', 'to': u"orm['makam.Artist']"}),
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'makam_release_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'is_concert': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'makam_release_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'makam_release_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tracks': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['makam.Recording']", 'through': u"orm['makam.ReleaseRecording']", 'symmetrical': 'False'}),
            'year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'makam.releaserecording': {
            'Meta': {'object_name': 'ReleaseRecording'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['makam.Recording']"}),
            'release': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['makam.Release']"}),
            'track': ('django.db.models.fields.IntegerField', [], {})
        },
        u'makam.usul': {
            'Meta': {'object_name': 'Usul'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'makam.usulalias': {
            'Meta': {'object_name': 'UsulAlias'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'usul': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'to': u"orm['makam.Usul']"})
        },
        u'makam.work': {
            'Meta': {'object_name': 'Work'},
            'composers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'works'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['makam.Composer']"}),
            'composition_date': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            'form': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['makam.Form']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'makam_work_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'is_taksim': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lyricists': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'lyric_works'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['makam.Composer']"}),
            'makam': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['makam.Makam']", 'null': 'True', 'blank': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'makam_work_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'makam_work_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'usul': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['makam.Usul']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['makam']