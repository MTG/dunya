# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GeographicRegion'
        db.create_table(u'carnatic_geographicregion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'carnatic', ['GeographicRegion'])

        # Adding model 'MusicalSchool'
        db.create_table(u'carnatic_musicalschool', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'carnatic', ['MusicalSchool'])

        # Adding model 'Artist'
        db.create_table(u'carnatic_artist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'carnatic_artist_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('begin', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('end', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('artist_type', self.gf('django.db.models.fields.CharField')(default='P', max_length=1)),
            ('main_instrument', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Instrument'], null=True, blank=True)),
            ('dummy', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.GeographicRegion'], null=True, blank=True)),
            ('hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'carnatic', ['Artist'])

        # Adding M2M table for field references on 'Artist'
        m2m_table_name = db.shorten_name(u'carnatic_artist_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('artist', models.ForeignKey(orm[u'carnatic.artist'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['artist_id', 'source_id'])

        # Adding M2M table for field images on 'Artist'
        m2m_table_name = db.shorten_name(u'carnatic_artist_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('artist', models.ForeignKey(orm[u'carnatic.artist'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['artist_id', 'image_id'])

        # Adding M2M table for field group_members on 'Artist'
        m2m_table_name = db.shorten_name(u'carnatic_artist_group_members')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_artist', models.ForeignKey(orm[u'carnatic.artist'], null=False)),
            ('to_artist', models.ForeignKey(orm[u'carnatic.artist'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_artist_id', 'to_artist_id'])

        # Adding M2M table for field gurus on 'Artist'
        m2m_table_name = db.shorten_name(u'carnatic_artist_gurus')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_artist', models.ForeignKey(orm[u'carnatic.artist'], null=False)),
            ('to_artist', models.ForeignKey(orm[u'carnatic.artist'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_artist_id', 'to_artist_id'])

        # Adding model 'Language'
        db.create_table(u'carnatic_language', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'carnatic', ['Language'])

        # Adding model 'LanguageAlias'
        db.create_table(u'carnatic_languagealias', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(related_name='aliases', to=orm['carnatic.Language'])),
        ))
        db.send_create_signal(u'carnatic', ['LanguageAlias'])

        # Adding model 'Sabbah'
        db.create_table(u'carnatic_sabbah', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'carnatic', ['Sabbah'])

        # Adding model 'ConcertRecording'
        db.create_table(u'carnatic_concertrecording', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('concert', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Concert'])),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Recording'])),
            ('track', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'carnatic', ['ConcertRecording'])

        # Adding model 'Concert'
        db.create_table(u'carnatic_concert', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'carnatic_concert_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('artistcredit', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('year', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('sabbah', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Sabbah'], null=True, blank=True)),
        ))
        db.send_create_signal(u'carnatic', ['Concert'])

        # Adding M2M table for field references on 'Concert'
        m2m_table_name = db.shorten_name(u'carnatic_concert_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('concert', models.ForeignKey(orm[u'carnatic.concert'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['concert_id', 'source_id'])

        # Adding M2M table for field images on 'Concert'
        m2m_table_name = db.shorten_name(u'carnatic_concert_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('concert', models.ForeignKey(orm[u'carnatic.concert'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['concert_id', 'image_id'])

        # Adding M2M table for field artists on 'Concert'
        m2m_table_name = db.shorten_name(u'carnatic_concert_artists')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('concert', models.ForeignKey(orm[u'carnatic.concert'], null=False)),
            ('artist', models.ForeignKey(orm[u'carnatic.artist'], null=False))
        ))
        db.create_unique(m2m_table_name, ['concert_id', 'artist_id'])

        # Adding model 'RaagaAlias'
        db.create_table(u'carnatic_raagaalias', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('raaga', self.gf('django.db.models.fields.related.ForeignKey')(related_name='aliases', to=orm['carnatic.Raaga'])),
        ))
        db.send_create_signal(u'carnatic', ['RaagaAlias'])

        # Adding model 'Form'
        db.create_table(u'carnatic_form', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'carnatic', ['Form'])

        # Adding model 'FormAlias'
        db.create_table(u'carnatic_formalias', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('form', self.gf('django.db.models.fields.related.ForeignKey')(related_name='aliases', to=orm['carnatic.Form'])),
        ))
        db.send_create_signal(u'carnatic', ['FormAlias'])

        # Adding model 'Raaga'
        db.create_table(u'carnatic_raaga', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'carnatic_raaga_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('transliteration', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'carnatic', ['Raaga'])

        # Adding M2M table for field references on 'Raaga'
        m2m_table_name = db.shorten_name(u'carnatic_raaga_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('raaga', models.ForeignKey(orm[u'carnatic.raaga'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['raaga_id', 'source_id'])

        # Adding M2M table for field images on 'Raaga'
        m2m_table_name = db.shorten_name(u'carnatic_raaga_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('raaga', models.ForeignKey(orm[u'carnatic.raaga'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['raaga_id', 'image_id'])

        # Adding model 'TaalaAlias'
        db.create_table(u'carnatic_taalaalias', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('taala', self.gf('django.db.models.fields.related.ForeignKey')(related_name='aliases', to=orm['carnatic.Taala'])),
        ))
        db.send_create_signal(u'carnatic', ['TaalaAlias'])

        # Adding model 'Taala'
        db.create_table(u'carnatic_taala', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'carnatic_taala_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('transliteration', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'carnatic', ['Taala'])

        # Adding M2M table for field references on 'Taala'
        m2m_table_name = db.shorten_name(u'carnatic_taala_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('taala', models.ForeignKey(orm[u'carnatic.taala'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['taala_id', 'source_id'])

        # Adding M2M table for field images on 'Taala'
        m2m_table_name = db.shorten_name(u'carnatic_taala_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('taala', models.ForeignKey(orm[u'carnatic.taala'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['taala_id', 'image_id'])

        # Adding model 'Work'
        db.create_table(u'carnatic_work', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'carnatic_work_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('composer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Composer'], null=True, blank=True)),
            ('form', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Form'], null=True, blank=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Language'], null=True, blank=True)),
        ))
        db.send_create_signal(u'carnatic', ['Work'])

        # Adding M2M table for field references on 'Work'
        m2m_table_name = db.shorten_name(u'carnatic_work_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('work', models.ForeignKey(orm[u'carnatic.work'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['work_id', 'source_id'])

        # Adding M2M table for field images on 'Work'
        m2m_table_name = db.shorten_name(u'carnatic_work_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('work', models.ForeignKey(orm[u'carnatic.work'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['work_id', 'image_id'])

        # Adding model 'WorkRaaga'
        db.create_table(u'carnatic_workraaga', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('work', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Work'])),
            ('raaga', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Raaga'])),
            ('sequence', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'carnatic', ['WorkRaaga'])

        # Adding model 'WorkTaala'
        db.create_table(u'carnatic_worktaala', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('work', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Work'])),
            ('taala', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Taala'])),
            ('sequence', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'carnatic', ['WorkTaala'])

        # Adding model 'Recording'
        db.create_table(u'carnatic_recording', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'carnatic_recording_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('length', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('work', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Work'], null=True, blank=True)),
        ))
        db.send_create_signal(u'carnatic', ['Recording'])

        # Adding M2M table for field references on 'Recording'
        m2m_table_name = db.shorten_name(u'carnatic_recording_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('recording', models.ForeignKey(orm[u'carnatic.recording'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['recording_id', 'source_id'])

        # Adding M2M table for field images on 'Recording'
        m2m_table_name = db.shorten_name(u'carnatic_recording_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('recording', models.ForeignKey(orm[u'carnatic.recording'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['recording_id', 'image_id'])

        # Adding model 'InstrumentAlias'
        db.create_table(u'carnatic_instrumentalias', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('instrument', self.gf('django.db.models.fields.related.ForeignKey')(related_name='aliases', to=orm['carnatic.Instrument'])),
        ))
        db.send_create_signal(u'carnatic', ['InstrumentAlias'])

        # Adding model 'Instrument'
        db.create_table(u'carnatic_instrument', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'carnatic_instrument_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('percussion', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'carnatic', ['Instrument'])

        # Adding M2M table for field references on 'Instrument'
        m2m_table_name = db.shorten_name(u'carnatic_instrument_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('instrument', models.ForeignKey(orm[u'carnatic.instrument'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['instrument_id', 'source_id'])

        # Adding M2M table for field images on 'Instrument'
        m2m_table_name = db.shorten_name(u'carnatic_instrument_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('instrument', models.ForeignKey(orm[u'carnatic.instrument'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['instrument_id', 'image_id'])

        # Adding model 'InstrumentPerformance'
        db.create_table(u'carnatic_instrumentperformance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Recording'])),
            ('performer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Artist'])),
            ('instrument', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Instrument'])),
            ('lead', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'carnatic', ['InstrumentPerformance'])

        # Adding model 'InstrumentConcertPerformance'
        db.create_table(u'carnatic_instrumentconcertperformance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('concert', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Concert'])),
            ('performer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Artist'])),
            ('instrument', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Instrument'])),
            ('lead', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'carnatic', ['InstrumentConcertPerformance'])

        # Adding model 'Composer'
        db.create_table(u'carnatic_composer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'carnatic_composer_source_set', null=True, to=orm['data.Source'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['data.Description'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('begin', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('end', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.GeographicRegion'], null=True, blank=True)),
        ))
        db.send_create_signal(u'carnatic', ['Composer'])

        # Adding M2M table for field references on 'Composer'
        m2m_table_name = db.shorten_name(u'carnatic_composer_references')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('composer', models.ForeignKey(orm[u'carnatic.composer'], null=False)),
            ('source', models.ForeignKey(orm[u'data.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['composer_id', 'source_id'])

        # Adding M2M table for field images on 'Composer'
        m2m_table_name = db.shorten_name(u'carnatic_composer_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('composer', models.ForeignKey(orm[u'carnatic.composer'], null=False)),
            ('image', models.ForeignKey(orm[u'data.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['composer_id', 'image_id'])


    def backwards(self, orm):
        # Deleting model 'GeographicRegion'
        db.delete_table(u'carnatic_geographicregion')

        # Deleting model 'MusicalSchool'
        db.delete_table(u'carnatic_musicalschool')

        # Deleting model 'Artist'
        db.delete_table(u'carnatic_artist')

        # Removing M2M table for field references on 'Artist'
        db.delete_table(db.shorten_name(u'carnatic_artist_references'))

        # Removing M2M table for field images on 'Artist'
        db.delete_table(db.shorten_name(u'carnatic_artist_images'))

        # Removing M2M table for field group_members on 'Artist'
        db.delete_table(db.shorten_name(u'carnatic_artist_group_members'))

        # Removing M2M table for field gurus on 'Artist'
        db.delete_table(db.shorten_name(u'carnatic_artist_gurus'))

        # Deleting model 'Language'
        db.delete_table(u'carnatic_language')

        # Deleting model 'LanguageAlias'
        db.delete_table(u'carnatic_languagealias')

        # Deleting model 'Sabbah'
        db.delete_table(u'carnatic_sabbah')

        # Deleting model 'ConcertRecording'
        db.delete_table(u'carnatic_concertrecording')

        # Deleting model 'Concert'
        db.delete_table(u'carnatic_concert')

        # Removing M2M table for field references on 'Concert'
        db.delete_table(db.shorten_name(u'carnatic_concert_references'))

        # Removing M2M table for field images on 'Concert'
        db.delete_table(db.shorten_name(u'carnatic_concert_images'))

        # Removing M2M table for field artists on 'Concert'
        db.delete_table(db.shorten_name(u'carnatic_concert_artists'))

        # Deleting model 'RaagaAlias'
        db.delete_table(u'carnatic_raagaalias')

        # Deleting model 'Form'
        db.delete_table(u'carnatic_form')

        # Deleting model 'FormAlias'
        db.delete_table(u'carnatic_formalias')

        # Deleting model 'Raaga'
        db.delete_table(u'carnatic_raaga')

        # Removing M2M table for field references on 'Raaga'
        db.delete_table(db.shorten_name(u'carnatic_raaga_references'))

        # Removing M2M table for field images on 'Raaga'
        db.delete_table(db.shorten_name(u'carnatic_raaga_images'))

        # Deleting model 'TaalaAlias'
        db.delete_table(u'carnatic_taalaalias')

        # Deleting model 'Taala'
        db.delete_table(u'carnatic_taala')

        # Removing M2M table for field references on 'Taala'
        db.delete_table(db.shorten_name(u'carnatic_taala_references'))

        # Removing M2M table for field images on 'Taala'
        db.delete_table(db.shorten_name(u'carnatic_taala_images'))

        # Deleting model 'Work'
        db.delete_table(u'carnatic_work')

        # Removing M2M table for field references on 'Work'
        db.delete_table(db.shorten_name(u'carnatic_work_references'))

        # Removing M2M table for field images on 'Work'
        db.delete_table(db.shorten_name(u'carnatic_work_images'))

        # Deleting model 'WorkRaaga'
        db.delete_table(u'carnatic_workraaga')

        # Deleting model 'WorkTaala'
        db.delete_table(u'carnatic_worktaala')

        # Deleting model 'Recording'
        db.delete_table(u'carnatic_recording')

        # Removing M2M table for field references on 'Recording'
        db.delete_table(db.shorten_name(u'carnatic_recording_references'))

        # Removing M2M table for field images on 'Recording'
        db.delete_table(db.shorten_name(u'carnatic_recording_images'))

        # Deleting model 'InstrumentAlias'
        db.delete_table(u'carnatic_instrumentalias')

        # Deleting model 'Instrument'
        db.delete_table(u'carnatic_instrument')

        # Removing M2M table for field references on 'Instrument'
        db.delete_table(db.shorten_name(u'carnatic_instrument_references'))

        # Removing M2M table for field images on 'Instrument'
        db.delete_table(db.shorten_name(u'carnatic_instrument_images'))

        # Deleting model 'InstrumentPerformance'
        db.delete_table(u'carnatic_instrumentperformance')

        # Deleting model 'InstrumentConcertPerformance'
        db.delete_table(u'carnatic_instrumentconcertperformance')

        # Deleting model 'Composer'
        db.delete_table(u'carnatic_composer')

        # Removing M2M table for field references on 'Composer'
        db.delete_table(db.shorten_name(u'carnatic_composer_references'))

        # Removing M2M table for field images on 'Composer'
        db.delete_table(db.shorten_name(u'carnatic_composer_images'))


    models = {
        u'carnatic.artist': {
            'Meta': {'object_name': 'Artist'},
            'artist_type': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '1'}),
            'begin': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            'dummy': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'group_members': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'groups'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['carnatic.Artist']"}),
            'gurus': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'students'", 'symmetrical': 'False', 'to': u"orm['carnatic.Artist']"}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'carnatic_artist_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'main_instrument': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Instrument']", 'null': 'True', 'blank': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'carnatic_artist_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'carnatic_artist_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.GeographicRegion']", 'null': 'True', 'blank': 'True'})
        },
        u'carnatic.composer': {
            'Meta': {'object_name': 'Composer'},
            'begin': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            'end': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'carnatic_composer_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'carnatic_composer_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'carnatic_composer_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.GeographicRegion']", 'null': 'True', 'blank': 'True'})
        },
        u'carnatic.concert': {
            'Meta': {'object_name': 'Concert'},
            'artistcredit': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'artists': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'primary_concerts'", 'symmetrical': 'False', 'to': u"orm['carnatic.Artist']"}),
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'carnatic_concert_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'performance': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'accompanying_concerts'", 'symmetrical': 'False', 'through': u"orm['carnatic.InstrumentConcertPerformance']", 'to': u"orm['carnatic.Artist']"}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'carnatic_concert_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'sabbah': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Sabbah']", 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'carnatic_concert_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tracks': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['carnatic.Recording']", 'through': u"orm['carnatic.ConcertRecording']", 'symmetrical': 'False'}),
            'year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'carnatic.concertrecording': {
            'Meta': {'object_name': 'ConcertRecording'},
            'concert': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Concert']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Recording']"}),
            'track': ('django.db.models.fields.IntegerField', [], {})
        },
        u'carnatic.form': {
            'Meta': {'object_name': 'Form'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'carnatic.formalias': {
            'Meta': {'object_name': 'FormAlias'},
            'form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'to': u"orm['carnatic.Form']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'carnatic.geographicregion': {
            'Meta': {'object_name': 'GeographicRegion'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'carnatic.instrument': {
            'Meta': {'object_name': 'Instrument'},
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'carnatic_instrument_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'percussion': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'carnatic_instrument_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'carnatic_instrument_source_set'", 'null': 'True', 'to': u"orm['data.Source']"})
        },
        u'carnatic.instrumentalias': {
            'Meta': {'object_name': 'InstrumentAlias'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instrument': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'to': u"orm['carnatic.Instrument']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'carnatic.instrumentconcertperformance': {
            'Meta': {'object_name': 'InstrumentConcertPerformance'},
            'concert': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Concert']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instrument': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Instrument']"}),
            'lead': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'performer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Artist']"})
        },
        u'carnatic.instrumentperformance': {
            'Meta': {'object_name': 'InstrumentPerformance'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instrument': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Instrument']"}),
            'lead': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'performer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Artist']"}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Recording']"})
        },
        u'carnatic.language': {
            'Meta': {'object_name': 'Language'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'carnatic.languagealias': {
            'Meta': {'object_name': 'LanguageAlias'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'to': u"orm['carnatic.Language']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'carnatic.musicalschool': {
            'Meta': {'object_name': 'MusicalSchool'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'carnatic.raaga': {
            'Meta': {'object_name': 'Raaga'},
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'carnatic_raaga_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'carnatic_raaga_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'carnatic_raaga_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'transliteration': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'carnatic.raagaalias': {
            'Meta': {'object_name': 'RaagaAlias'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'raaga': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'to': u"orm['carnatic.Raaga']"})
        },
        u'carnatic.recording': {
            'Meta': {'object_name': 'Recording'},
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'carnatic_recording_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'length': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'performance': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['carnatic.Artist']", 'through': u"orm['carnatic.InstrumentPerformance']", 'symmetrical': 'False'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'carnatic_recording_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'carnatic_recording_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Work']", 'null': 'True', 'blank': 'True'})
        },
        u'carnatic.sabbah': {
            'Meta': {'object_name': 'Sabbah'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'carnatic.taala': {
            'Meta': {'object_name': 'Taala'},
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'carnatic_taala_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'carnatic_taala_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'carnatic_taala_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'transliteration': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'carnatic.taalaalias': {
            'Meta': {'object_name': 'TaalaAlias'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'taala': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'to': u"orm['carnatic.Taala']"})
        },
        u'carnatic.work': {
            'Meta': {'object_name': 'Work'},
            'composer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Composer']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['data.Description']"}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Form']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'carnatic_work_image_set'", 'symmetrical': 'False', 'to': u"orm['data.Image']"}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Language']", 'null': 'True', 'blank': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'raaga': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['carnatic.Raaga']", 'through': u"orm['carnatic.WorkRaaga']", 'symmetrical': 'False'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'carnatic_work_reference_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['data.Source']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'carnatic_work_source_set'", 'null': 'True', 'to': u"orm['data.Source']"}),
            'taala': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['carnatic.Taala']", 'through': u"orm['carnatic.WorkTaala']", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'carnatic.workraaga': {
            'Meta': {'object_name': 'WorkRaaga'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'raaga': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Raaga']"}),
            'sequence': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Work']"})
        },
        u'carnatic.worktaala': {
            'Meta': {'object_name': 'WorkTaala'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sequence': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'taala': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Taala']"}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Work']"})
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

    complete_apps = ['carnatic']