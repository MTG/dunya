# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MusicalSchool'
        db.create_table(u'andalusian_musicalschool', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'andalusian_musicalschool_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('transliterated_name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'andalusian', ['MusicalSchool'])

        # Adding M2M table for field references on 'MusicalSchool'
        m2m_table_name = db.shorten_name(u'andalusian_musicalschool_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('musicalschool', models.ForeignKey(orm[u'andalusian.musicalschool'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['musicalschool_id', 'source_id'])

        # Adding M2M table for field images on 'MusicalSchool'
        m2m_table_name = db.shorten_name(u'andalusian_musicalschool_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('musicalschool', models.ForeignKey(orm[u'andalusian.musicalschool'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['musicalschool_id', 'image_id'])

        # Adding model 'Orchestra'
        db.create_table(u'andalusian_orchestra', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'andalusian_orchestra_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('transliterated_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.MusicalSchool'], null=True, blank=True)),
        ))
        db.send_create_signal(u'andalusian', ['Orchestra'])

        # Adding M2M table for field references on 'Orchestra'
        m2m_table_name = db.shorten_name(u'andalusian_orchestra_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('orchestra', models.ForeignKey(orm[u'andalusian.orchestra'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['orchestra_id', 'source_id'])

        # Adding M2M table for field images on 'Orchestra'
        m2m_table_name = db.shorten_name(u'andalusian_orchestra_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('orchestra', models.ForeignKey(orm[u'andalusian.orchestra'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['orchestra_id', 'image_id'])

        # Adding model 'OrchestraAlias'
        db.create_table(u'andalusian_orchestraalias', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('orchestra', self.gf('django.db.models.fields.related.ForeignKey')(related_name='aliases', to=orm['andalusian.Orchestra'])),
        ))
        db.send_create_signal(u'andalusian', ['OrchestraAlias'])

        # Adding model 'Artist'
        db.create_table(u'andalusian_artist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'andalusian_artist_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('transliterated_name', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('begin', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('end', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
        ))
        db.send_create_signal(u'andalusian', ['Artist'])

        # Adding M2M table for field references on 'Artist'
        m2m_table_name = db.shorten_name(u'andalusian_artist_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('artist', models.ForeignKey(orm[u'andalusian.artist'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['artist_id', 'source_id'])

        # Adding M2M table for field images on 'Artist'
        m2m_table_name = db.shorten_name(u'andalusian_artist_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('artist', models.ForeignKey(orm[u'andalusian.artist'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['artist_id', 'image_id'])

        # Adding model 'ArtistAlias'
        db.create_table(u'andalusian_artistalias', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(related_name='aliases', to=orm['andalusian.Artist'])),
        ))
        db.send_create_signal(u'andalusian', ['ArtistAlias'])

        # Adding model 'AlbumType'
        db.create_table(u'andalusian_albumtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('transliterated_type', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'andalusian', ['AlbumType'])

        # Adding model 'AlbumRecording'
        db.create_table(u'andalusian_albumrecording', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('album', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.Album'])),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.Recording'])),
            ('track', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'andalusian', ['AlbumRecording'])

        # Adding model 'Album'
        db.create_table(u'andalusian_album', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'andalusian_album_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('transliterated_title', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('album_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.AlbumType'], null=True, blank=True)),
            ('director', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.Artist'], null=True)),
        ))
        db.send_create_signal(u'andalusian', ['Album'])

        # Adding M2M table for field references on 'Album'
        m2m_table_name = db.shorten_name(u'andalusian_album_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('album', models.ForeignKey(orm[u'andalusian.album'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['album_id', 'source_id'])

        # Adding M2M table for field images on 'Album'
        m2m_table_name = db.shorten_name(u'andalusian_album_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('album', models.ForeignKey(orm[u'andalusian.album'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['album_id', 'image_id'])

        # Adding M2M table for field artists on 'Album'
        m2m_table_name = db.shorten_name(u'andalusian_album_artists')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('album', models.ForeignKey(orm[u'andalusian.album'], null=False)),
            ('orchestra', models.ForeignKey(orm[u'andalusian.orchestra'], null=False))
        ))
        db.create_unique(m2m_table_name, ['album_id', 'orchestra_id'])

        # Adding model 'Work'
        db.create_table(u'andalusian_work', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'andalusian_work_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('transliterated_title', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'andalusian', ['Work'])

        # Adding M2M table for field references on 'Work'
        m2m_table_name = db.shorten_name(u'andalusian_work_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('work', models.ForeignKey(orm[u'andalusian.work'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['work_id', 'source_id'])

        # Adding M2M table for field images on 'Work'
        m2m_table_name = db.shorten_name(u'andalusian_work_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('work', models.ForeignKey(orm[u'andalusian.work'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['work_id', 'image_id'])

        # Adding model 'Genre'
        db.create_table(u'andalusian_genre', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'andalusian_genre_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('transliterated_name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'andalusian', ['Genre'])

        # Adding M2M table for field references on 'Genre'
        m2m_table_name = db.shorten_name(u'andalusian_genre_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('genre', models.ForeignKey(orm[u'andalusian.genre'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['genre_id', 'source_id'])

        # Adding M2M table for field images on 'Genre'
        m2m_table_name = db.shorten_name(u'andalusian_genre_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('genre', models.ForeignKey(orm[u'andalusian.genre'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['genre_id', 'image_id'])

        # Adding model 'RecordingWork'
        db.create_table(u'andalusian_recordingwork', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('work', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.Work'])),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.Recording'])),
            ('sequence', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'andalusian', ['RecordingWork'])

        # Adding model 'Recording'
        db.create_table(u'andalusian_recording', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'andalusian_recording_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('transliterated_title', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('length', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('year', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('genre', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.Genre'], null=True)),
        ))
        db.send_create_signal(u'andalusian', ['Recording'])

        # Adding M2M table for field references on 'Recording'
        m2m_table_name = db.shorten_name(u'andalusian_recording_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('recording', models.ForeignKey(orm[u'andalusian.recording'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['recording_id', 'source_id'])

        # Adding M2M table for field images on 'Recording'
        m2m_table_name = db.shorten_name(u'andalusian_recording_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('recording', models.ForeignKey(orm[u'andalusian.recording'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['recording_id', 'image_id'])

        # Adding model 'Instrument'
        db.create_table(u'andalusian_instrument', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'andalusian_instrument_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('percussion', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('original_name', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
        ))
        db.send_create_signal(u'andalusian', ['Instrument'])

        # Adding M2M table for field references on 'Instrument'
        m2m_table_name = db.shorten_name(u'andalusian_instrument_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('instrument', models.ForeignKey(orm[u'andalusian.instrument'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['instrument_id', 'source_id'])

        # Adding M2M table for field images on 'Instrument'
        m2m_table_name = db.shorten_name(u'andalusian_instrument_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('instrument', models.ForeignKey(orm[u'andalusian.instrument'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['instrument_id', 'image_id'])

        # Adding model 'InstrumentPerformance'
        db.create_table(u'andalusian_instrumentperformance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.Recording'])),
            ('performer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.Artist'])),
            ('instrument', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.Instrument'])),
            ('lead', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'andalusian', ['InstrumentPerformance'])

        # Adding model 'OrchestraPerformer'
        db.create_table(u'andalusian_orchestraperformer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('orchestra', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.Orchestra'])),
            ('performer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.Artist'])),
            ('director', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('begin', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('end', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
        ))
        db.send_create_signal(u'andalusian', ['OrchestraPerformer'])

        # Adding M2M table for field instruments on 'OrchestraPerformer'
        m2m_table_name = db.shorten_name(u'andalusian_orchestraperformer_instruments')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('orchestraperformer', models.ForeignKey(orm[u'andalusian.orchestraperformer'], null=False)),
            ('instrument', models.ForeignKey(orm[u'andalusian.instrument'], null=False))
        ))
        db.create_unique(m2m_table_name, ['orchestraperformer_id', 'instrument_id'])

        # Adding model 'Tab'
        db.create_table(u'andalusian_tab', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'andalusian_tab_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('transliterated_name', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
        ))
        db.send_create_signal(u'andalusian', ['Tab'])

        # Adding M2M table for field references on 'Tab'
        m2m_table_name = db.shorten_name(u'andalusian_tab_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tab', models.ForeignKey(orm[u'andalusian.tab'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['tab_id', 'source_id'])

        # Adding M2M table for field images on 'Tab'
        m2m_table_name = db.shorten_name(u'andalusian_tab_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tab', models.ForeignKey(orm[u'andalusian.tab'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['tab_id', 'image_id'])

        # Adding model 'Nawba'
        db.create_table(u'andalusian_nawba', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'andalusian_nawba_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('transliterated_name', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
        ))
        db.send_create_signal(u'andalusian', ['Nawba'])

        # Adding M2M table for field references on 'Nawba'
        m2m_table_name = db.shorten_name(u'andalusian_nawba_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('nawba', models.ForeignKey(orm[u'andalusian.nawba'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['nawba_id', 'source_id'])

        # Adding M2M table for field images on 'Nawba'
        m2m_table_name = db.shorten_name(u'andalusian_nawba_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('nawba', models.ForeignKey(orm[u'andalusian.nawba'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['nawba_id', 'image_id'])

        # Adding model 'Mizan'
        db.create_table(u'andalusian_mizan', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'andalusian_mizan_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('transliterated_name', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
        ))
        db.send_create_signal(u'andalusian', ['Mizan'])

        # Adding M2M table for field references on 'Mizan'
        m2m_table_name = db.shorten_name(u'andalusian_mizan_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mizan', models.ForeignKey(orm[u'andalusian.mizan'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['mizan_id', 'source_id'])

        # Adding M2M table for field images on 'Mizan'
        m2m_table_name = db.shorten_name(u'andalusian_mizan_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mizan', models.ForeignKey(orm[u'andalusian.mizan'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['mizan_id', 'image_id'])

        # Adding model 'FormType'
        db.create_table(u'andalusian_formtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'andalusian', ['FormType'])

        # Adding model 'Form'
        db.create_table(u'andalusian_form', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'andalusian_form_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('transliterated_name', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('form_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.FormType'], null=True, blank=True)),
        ))
        db.send_create_signal(u'andalusian', ['Form'])

        # Adding M2M table for field references on 'Form'
        m2m_table_name = db.shorten_name(u'andalusian_form_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('form', models.ForeignKey(orm[u'andalusian.form'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['form_id', 'source_id'])

        # Adding M2M table for field images on 'Form'
        m2m_table_name = db.shorten_name(u'andalusian_form_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('form', models.ForeignKey(orm[u'andalusian.form'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['form_id', 'image_id'])

        # Adding model 'Section'
        db.create_table(u'andalusian_section', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'andalusian_section_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.Recording'])),
            ('start_time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('end_time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('tab', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.Tab'], null=True, blank=True)),
            ('nawba', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.Nawba'], null=True, blank=True)),
            ('mizan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.Mizan'], null=True, blank=True)),
            ('form', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.Form'], null=True, blank=True)),
        ))
        db.send_create_signal(u'andalusian', ['Section'])

        # Adding M2M table for field references on 'Section'
        m2m_table_name = db.shorten_name(u'andalusian_section_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('section', models.ForeignKey(orm[u'andalusian.section'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['section_id', 'source_id'])

        # Adding M2M table for field images on 'Section'
        m2m_table_name = db.shorten_name(u'andalusian_section_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('section', models.ForeignKey(orm[u'andalusian.section'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['section_id', 'image_id'])

        # Adding model 'InstrumentSectionPerformance'
        db.create_table(u'andalusian_instrumentsectionperformance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.Section'])),
            ('performer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.Artist'])),
            ('instrument', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.Instrument'])),
            ('lead', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'andalusian', ['InstrumentSectionPerformance'])

        # Adding model 'Sanaa'
        db.create_table(u'andalusian_sanaa', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'andalusian_sanaa_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('transliterated_title', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'andalusian', ['Sanaa'])

        # Adding M2M table for field references on 'Sanaa'
        m2m_table_name = db.shorten_name(u'andalusian_sanaa_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sanaa', models.ForeignKey(orm[u'andalusian.sanaa'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['sanaa_id', 'source_id'])

        # Adding M2M table for field images on 'Sanaa'
        m2m_table_name = db.shorten_name(u'andalusian_sanaa_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sanaa', models.ForeignKey(orm[u'andalusian.sanaa'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['sanaa_id', 'image_id'])

        # Adding model 'PoemType'
        db.create_table(u'andalusian_poemtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'andalusian', ['PoemType'])

        # Adding model 'Poem'
        db.create_table(u'andalusian_poem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'andalusian_poem_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('identifier', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('first_words', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('transliterated_first_words', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.PoemType'], null=True, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('transliterated_text', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'andalusian', ['Poem'])

        # Adding M2M table for field references on 'Poem'
        m2m_table_name = db.shorten_name(u'andalusian_poem_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('poem', models.ForeignKey(orm[u'andalusian.poem'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['poem_id', 'source_id'])

        # Adding M2M table for field images on 'Poem'
        m2m_table_name = db.shorten_name(u'andalusian_poem_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('poem', models.ForeignKey(orm[u'andalusian.poem'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['poem_id', 'image_id'])

        # Adding model 'SectionSanaaPoem'
        db.create_table(u'andalusian_sectionsanaapoem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.Section'])),
            ('sanaa', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.Sanaa'])),
            ('poem', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['andalusian.Poem'])),
            ('order_number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'andalusian', ['SectionSanaaPoem'])


    def backwards(self, orm):
        # Deleting model 'MusicalSchool'
        db.delete_table(u'andalusian_musicalschool')

        # Removing M2M table for field references on 'MusicalSchool'
        db.delete_table(db.shorten_name(u'andalusian_musicalschool_references'))

        # Removing M2M table for field images on 'MusicalSchool'
        db.delete_table(db.shorten_name(u'andalusian_musicalschool_images'))

        # Deleting model 'Orchestra'
        db.delete_table(u'andalusian_orchestra')

        # Removing M2M table for field references on 'Orchestra'
        db.delete_table(db.shorten_name(u'andalusian_orchestra_references'))

        # Removing M2M table for field images on 'Orchestra'
        db.delete_table(db.shorten_name(u'andalusian_orchestra_images'))

        # Deleting model 'OrchestraAlias'
        db.delete_table(u'andalusian_orchestraalias')

        # Deleting model 'Artist'
        db.delete_table(u'andalusian_artist')

        # Removing M2M table for field references on 'Artist'
        db.delete_table(db.shorten_name(u'andalusian_artist_references'))

        # Removing M2M table for field images on 'Artist'
        db.delete_table(db.shorten_name(u'andalusian_artist_images'))

        # Deleting model 'ArtistAlias'
        db.delete_table(u'andalusian_artistalias')

        # Deleting model 'AlbumType'
        db.delete_table(u'andalusian_albumtype')

        # Deleting model 'AlbumRecording'
        db.delete_table(u'andalusian_albumrecording')

        # Deleting model 'Album'
        db.delete_table(u'andalusian_album')

        # Removing M2M table for field references on 'Album'
        db.delete_table(db.shorten_name(u'andalusian_album_references'))

        # Removing M2M table for field images on 'Album'
        db.delete_table(db.shorten_name(u'andalusian_album_images'))

        # Removing M2M table for field artists on 'Album'
        db.delete_table(db.shorten_name(u'andalusian_album_artists'))

        # Deleting model 'Work'
        db.delete_table(u'andalusian_work')

        # Removing M2M table for field references on 'Work'
        db.delete_table(db.shorten_name(u'andalusian_work_references'))

        # Removing M2M table for field images on 'Work'
        db.delete_table(db.shorten_name(u'andalusian_work_images'))

        # Deleting model 'Genre'
        db.delete_table(u'andalusian_genre')

        # Removing M2M table for field references on 'Genre'
        db.delete_table(db.shorten_name(u'andalusian_genre_references'))

        # Removing M2M table for field images on 'Genre'
        db.delete_table(db.shorten_name(u'andalusian_genre_images'))

        # Deleting model 'RecordingWork'
        db.delete_table(u'andalusian_recordingwork')

        # Deleting model 'Recording'
        db.delete_table(u'andalusian_recording')

        # Removing M2M table for field references on 'Recording'
        db.delete_table(db.shorten_name(u'andalusian_recording_references'))

        # Removing M2M table for field images on 'Recording'
        db.delete_table(db.shorten_name(u'andalusian_recording_images'))

        # Deleting model 'Instrument'
        db.delete_table(u'andalusian_instrument')

        # Removing M2M table for field references on 'Instrument'
        db.delete_table(db.shorten_name(u'andalusian_instrument_references'))

        # Removing M2M table for field images on 'Instrument'
        db.delete_table(db.shorten_name(u'andalusian_instrument_images'))

        # Deleting model 'InstrumentPerformance'
        db.delete_table(u'andalusian_instrumentperformance')

        # Deleting model 'OrchestraPerformer'
        db.delete_table(u'andalusian_orchestraperformer')

        # Removing M2M table for field instruments on 'OrchestraPerformer'
        db.delete_table(db.shorten_name(u'andalusian_orchestraperformer_instruments'))

        # Deleting model 'Tab'
        db.delete_table(u'andalusian_tab')

        # Removing M2M table for field references on 'Tab'
        db.delete_table(db.shorten_name(u'andalusian_tab_references'))

        # Removing M2M table for field images on 'Tab'
        db.delete_table(db.shorten_name(u'andalusian_tab_images'))

        # Deleting model 'Nawba'
        db.delete_table(u'andalusian_nawba')

        # Removing M2M table for field references on 'Nawba'
        db.delete_table(db.shorten_name(u'andalusian_nawba_references'))

        # Removing M2M table for field images on 'Nawba'
        db.delete_table(db.shorten_name(u'andalusian_nawba_images'))

        # Deleting model 'Mizan'
        db.delete_table(u'andalusian_mizan')

        # Removing M2M table for field references on 'Mizan'
        db.delete_table(db.shorten_name(u'andalusian_mizan_references'))

        # Removing M2M table for field images on 'Mizan'
        db.delete_table(db.shorten_name(u'andalusian_mizan_images'))

        # Deleting model 'FormType'
        db.delete_table(u'andalusian_formtype')

        # Deleting model 'Form'
        db.delete_table(u'andalusian_form')

        # Removing M2M table for field references on 'Form'
        db.delete_table(db.shorten_name(u'andalusian_form_references'))

        # Removing M2M table for field images on 'Form'
        db.delete_table(db.shorten_name(u'andalusian_form_images'))

        # Deleting model 'Section'
        db.delete_table(u'andalusian_section')

        # Removing M2M table for field references on 'Section'
        db.delete_table(db.shorten_name(u'andalusian_section_references'))

        # Removing M2M table for field images on 'Section'
        db.delete_table(db.shorten_name(u'andalusian_section_images'))

        # Deleting model 'InstrumentSectionPerformance'
        db.delete_table(u'andalusian_instrumentsectionperformance')

        # Deleting model 'Sanaa'
        db.delete_table(u'andalusian_sanaa')

        # Removing M2M table for field references on 'Sanaa'
        db.delete_table(db.shorten_name(u'andalusian_sanaa_references'))

        # Removing M2M table for field images on 'Sanaa'
        db.delete_table(db.shorten_name(u'andalusian_sanaa_images'))

        # Deleting model 'PoemType'
        db.delete_table(u'andalusian_poemtype')

        # Deleting model 'Poem'
        db.delete_table(u'andalusian_poem')

        # Removing M2M table for field references on 'Poem'
        db.delete_table(db.shorten_name(u'andalusian_poem_references'))

        # Removing M2M table for field images on 'Poem'
        db.delete_table(db.shorten_name(u'andalusian_poem_images'))

        # Deleting model 'SectionSanaaPoem'
        db.delete_table(u'andalusian_sectionsanaapoem')


    models = {
        u'andalusian.album': {
            'Meta': {'object_name': 'Album'},
            'album_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.AlbumType']", 'null': 'True', 'blank': 'True'}),
            'artists': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['andalusian.Orchestra']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            'director': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.Artist']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'andalusian_album_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'recordings': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['andalusian.Recording']", 'through': u"orm['andalusian.AlbumRecording']", 'symmetrical': 'False'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'andalusian_album_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'andalusian_album_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'transliterated_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'andalusian.albumrecording': {
            'Meta': {'ordering': "('track',)", 'object_name': 'AlbumRecording'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.Album']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.Recording']"}),
            'track': ('django.db.models.fields.IntegerField', [], {})
        },
        u'andalusian.albumtype': {
            'Meta': {'object_name': 'AlbumType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'transliterated_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'andalusian.artist': {
            'Meta': {'object_name': 'Artist'},
            'begin': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            'end': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'andalusian_artist_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'andalusian_artist_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'andalusian_artist_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'transliterated_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'andalusian.artistalias': {
            'Meta': {'object_name': 'ArtistAlias'},
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'to': u"orm['andalusian.Artist']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'andalusian.form': {
            'Meta': {'object_name': 'Form'},
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            'form_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.FormType']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'andalusian_form_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'andalusian_form_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'andalusian_form_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'transliterated_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'andalusian.formtype': {
            'Meta': {'object_name': 'FormType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'andalusian.genre': {
            'Meta': {'object_name': 'Genre'},
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'andalusian_genre_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'andalusian_genre_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'andalusian_genre_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'transliterated_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'andalusian.instrument': {
            'Meta': {'object_name': 'Instrument'},
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'andalusian_instrument_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'original_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'percussion': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'andalusian_instrument_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'andalusian_instrument_source_set'", 'null': 'True', 'to': u"orm['data.Source']"})
        },
        u'andalusian.instrumentperformance': {
            'Meta': {'object_name': 'InstrumentPerformance'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instrument': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.Instrument']"}),
            'lead': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'performer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.Artist']"}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.Recording']"})
        },
        u'andalusian.instrumentsectionperformance': {
            'Meta': {'object_name': 'InstrumentSectionPerformance'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instrument': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.Instrument']"}),
            'lead': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'performer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.Artist']"}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.Section']"})
        },
        u'andalusian.mizan': {
            'Meta': {'object_name': 'Mizan'},
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'andalusian_mizan_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'andalusian_mizan_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'andalusian_mizan_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'transliterated_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'andalusian.musicalschool': {
            'Meta': {'object_name': 'MusicalSchool'},
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'andalusian_musicalschool_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'andalusian_musicalschool_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'andalusian_musicalschool_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'transliterated_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'andalusian.nawba': {
            'Meta': {'object_name': 'Nawba'},
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'andalusian_nawba_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'andalusian_nawba_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'andalusian_nawba_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'transliterated_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'andalusian.orchestra': {
            'Meta': {'object_name': 'Orchestra'},
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            'group_members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'groups'", 'to': u"orm['andalusian.Artist']", 'through': u"orm['andalusian.OrchestraPerformer']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'andalusian_orchestra_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'andalusian_orchestra_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.MusicalSchool']", 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'andalusian_orchestra_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'transliterated_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'andalusian.orchestraalias': {
            'Meta': {'object_name': 'OrchestraAlias'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'orchestra': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'to': u"orm['andalusian.Orchestra']"})
        },
        u'andalusian.orchestraperformer': {
            'Meta': {'object_name': 'OrchestraPerformer'},
            'begin': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'director': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instruments': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['andalusian.Instrument']", 'symmetrical': 'False'}),
            'orchestra': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.Orchestra']"}),
            'performer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.Artist']"})
        },
        u'andalusian.poem': {
            'Meta': {'object_name': 'Poem'},
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            'first_words': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'andalusian_poem_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'andalusian_poem_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'andalusian_poem_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'transliterated_first_words': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'transliterated_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.PoemType']", 'null': 'True', 'blank': 'True'})
        },
        u'andalusian.poemtype': {
            'Meta': {'object_name': 'PoemType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'andalusian.recording': {
            'Meta': {'object_name': 'Recording'},
            'artists': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['andalusian.Artist']", 'through': u"orm['andalusian.InstrumentPerformance']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            'genre': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.Genre']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'andalusian_recording_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'length': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'andalusian_recording_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'andalusian_recording_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'transliterated_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'works': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['andalusian.Work']", 'through': u"orm['andalusian.RecordingWork']", 'symmetrical': 'False'}),
            'year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'andalusian.recordingwork': {
            'Meta': {'ordering': "('sequence',)", 'object_name': 'RecordingWork'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.Recording']"}),
            'sequence': ('django.db.models.fields.IntegerField', [], {}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.Work']"})
        },
        u'andalusian.sanaa': {
            'Meta': {'object_name': 'Sanaa'},
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'andalusian_sanaa_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'andalusian_sanaa_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'andalusian_sanaa_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'transliterated_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'andalusian.section': {
            'Meta': {'object_name': 'Section'},
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            'end_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.Form']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'andalusian_section_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'mizan': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.Mizan']", 'null': 'True', 'blank': 'True'}),
            'nawba': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.Nawba']", 'null': 'True', 'blank': 'True'}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.Recording']"}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'andalusian_section_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'andalusian_section_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'start_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'tab': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.Tab']", 'null': 'True', 'blank': 'True'})
        },
        u'andalusian.sectionsanaapoem': {
            'Meta': {'object_name': 'SectionSanaaPoem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'poem': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.Poem']"}),
            'sanaa': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.Sanaa']"}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['andalusian.Section']"})
        },
        u'andalusian.tab': {
            'Meta': {'object_name': 'Tab'},
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'andalusian_tab_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'andalusian_tab_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'andalusian_tab_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'transliterated_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'andalusian.work': {
            'Meta': {'object_name': 'Work'},
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'andalusian_work_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'andalusian_work_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'andalusian_work_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'transliterated_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
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
        }
    }

    complete_apps = ['andalusian']