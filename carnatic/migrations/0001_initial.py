# -*- coding: utf-8 -*-
import datetime
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
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.Source'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('begin', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('end', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('artist_type', self.gf('django.db.models.fields.CharField')(default='P', max_length=1)),
            ('main_instrument', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Instrument'], null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.GeographicRegion'], null=True, blank=True)),
        ))
        db.send_create_signal(u'carnatic', ['Artist'])

        # Adding M2M table for field references on 'Artist'
        db.create_table(u'carnatic_artist_references', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('artist', models.ForeignKey(orm[u'carnatic.artist'], null=False)),
            ('reference', models.ForeignKey(orm[u'data.reference'], null=False))
        ))
        db.create_unique(u'carnatic_artist_references', ['artist_id', 'reference_id'])

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

        # Adding model 'Concert'
        db.create_table(u'carnatic_concert', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.Source'], null=True, blank=True)),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Location'], null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('year', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('label', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.Label'], null=True, blank=True)),
            ('sabbah', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Sabbah'], null=True, blank=True)),
        ))
        db.send_create_signal(u'carnatic', ['Concert'])

        # Adding M2M table for field references on 'Concert'
        db.create_table(u'carnatic_concert_references', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('concert', models.ForeignKey(orm[u'carnatic.concert'], null=False)),
            ('reference', models.ForeignKey(orm[u'data.reference'], null=False))
        ))
        db.create_unique(u'carnatic_concert_references', ['concert_id', 'reference_id'])

        # Adding M2M table for field artists on 'Concert'
        db.create_table(u'carnatic_concert_artists', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('concert', models.ForeignKey(orm[u'carnatic.concert'], null=False)),
            ('artist', models.ForeignKey(orm[u'carnatic.artist'], null=False))
        ))
        db.create_unique(u'carnatic_concert_artists', ['concert_id', 'artist_id'])

        # Adding M2M table for field tracks on 'Concert'
        db.create_table(u'carnatic_concert_tracks', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('concert', models.ForeignKey(orm[u'carnatic.concert'], null=False)),
            ('recording', models.ForeignKey(orm[u'carnatic.recording'], null=False))
        ))
        db.create_unique(u'carnatic_concert_tracks', ['concert_id', 'recording_id'])

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
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'carnatic', ['Raaga'])

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
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'carnatic', ['Taala'])

        # Adding model 'Work'
        db.create_table(u'carnatic_work', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.Source'], null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('composer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Composer'], null=True, blank=True)),
        ))
        db.send_create_signal(u'carnatic', ['Work'])

        # Adding M2M table for field references on 'Work'
        db.create_table(u'carnatic_work_references', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('work', models.ForeignKey(orm[u'carnatic.work'], null=False)),
            ('reference', models.ForeignKey(orm[u'data.reference'], null=False))
        ))
        db.create_unique(u'carnatic_work_references', ['work_id', 'reference_id'])

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

        # Adding model 'WorkAttribute'
        db.create_table(u'carnatic_workattribute', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('work', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Work'])),
            ('attribute_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.WorkAttributeType'])),
            ('attribute_value_free', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('attribute_value', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.WorkAttributeTypeValue'], null=True, blank=True)),
        ))
        db.send_create_signal(u'carnatic', ['WorkAttribute'])

        # Adding model 'WorkAttributeType'
        db.create_table(u'carnatic_workattributetype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'carnatic', ['WorkAttributeType'])

        # Adding model 'WorkAttributeTypeValue'
        db.create_table(u'carnatic_workattributetypevalue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('attribute_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.WorkAttributeType'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'carnatic', ['WorkAttributeTypeValue'])

        # Adding model 'Recording'
        db.create_table(u'carnatic_recording', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.Source'], null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('work', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Work'], null=True, blank=True)),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('length', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'carnatic', ['Recording'])

        # Adding M2M table for field references on 'Recording'
        db.create_table(u'carnatic_recording_references', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('recording', models.ForeignKey(orm[u'carnatic.recording'], null=False)),
            ('reference', models.ForeignKey(orm[u'data.reference'], null=False))
        ))
        db.create_unique(u'carnatic_recording_references', ['recording_id', 'reference_id'])

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
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.Source'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'carnatic', ['Instrument'])

        # Adding M2M table for field references on 'Instrument'
        db.create_table(u'carnatic_instrument_references', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('instrument', models.ForeignKey(orm[u'carnatic.instrument'], null=False)),
            ('reference', models.ForeignKey(orm[u'data.reference'], null=False))
        ))
        db.create_unique(u'carnatic_instrument_references', ['instrument_id', 'reference_id'])

        # Adding model 'InstrumentPerformance'
        db.create_table(u'carnatic_instrumentperformance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Recording'])),
            ('performer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Artist'])),
            ('instrument', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Instrument'])),
            ('lead', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'carnatic', ['InstrumentPerformance'])

        # Adding model 'Composer'
        db.create_table(u'carnatic_composer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.Source'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('begin', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('end', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.GeographicRegion'], null=True, blank=True)),
        ))
        db.send_create_signal(u'carnatic', ['Composer'])

        # Adding M2M table for field references on 'Composer'
        db.create_table(u'carnatic_composer_references', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('composer', models.ForeignKey(orm[u'carnatic.composer'], null=False)),
            ('reference', models.ForeignKey(orm[u'data.reference'], null=False))
        ))
        db.create_unique(u'carnatic_composer_references', ['composer_id', 'reference_id'])

        # Adding model 'Location'
        db.create_table(u'carnatic_location', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.Source'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('region', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('lat', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('lng', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
        ))
        db.send_create_signal(u'carnatic', ['Location'])

        # Adding M2M table for field references on 'Location'
        db.create_table(u'carnatic_location_references', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('location', models.ForeignKey(orm[u'carnatic.location'], null=False)),
            ('reference', models.ForeignKey(orm[u'data.reference'], null=False))
        ))
        db.create_unique(u'carnatic_location_references', ['location_id', 'reference_id'])


    def backwards(self, orm):
        # Deleting model 'GeographicRegion'
        db.delete_table(u'carnatic_geographicregion')

        # Deleting model 'MusicalSchool'
        db.delete_table(u'carnatic_musicalschool')

        # Deleting model 'Artist'
        db.delete_table(u'carnatic_artist')

        # Removing M2M table for field references on 'Artist'
        db.delete_table('carnatic_artist_references')

        # Deleting model 'Language'
        db.delete_table(u'carnatic_language')

        # Deleting model 'LanguageAlias'
        db.delete_table(u'carnatic_languagealias')

        # Deleting model 'Sabbah'
        db.delete_table(u'carnatic_sabbah')

        # Deleting model 'Concert'
        db.delete_table(u'carnatic_concert')

        # Removing M2M table for field references on 'Concert'
        db.delete_table('carnatic_concert_references')

        # Removing M2M table for field artists on 'Concert'
        db.delete_table('carnatic_concert_artists')

        # Removing M2M table for field tracks on 'Concert'
        db.delete_table('carnatic_concert_tracks')

        # Deleting model 'RaagaAlias'
        db.delete_table(u'carnatic_raagaalias')

        # Deleting model 'Form'
        db.delete_table(u'carnatic_form')

        # Deleting model 'FormAlias'
        db.delete_table(u'carnatic_formalias')

        # Deleting model 'Raaga'
        db.delete_table(u'carnatic_raaga')

        # Deleting model 'TaalaAlias'
        db.delete_table(u'carnatic_taalaalias')

        # Deleting model 'Taala'
        db.delete_table(u'carnatic_taala')

        # Deleting model 'Work'
        db.delete_table(u'carnatic_work')

        # Removing M2M table for field references on 'Work'
        db.delete_table('carnatic_work_references')

        # Deleting model 'WorkRaaga'
        db.delete_table(u'carnatic_workraaga')

        # Deleting model 'WorkTaala'
        db.delete_table(u'carnatic_worktaala')

        # Deleting model 'WorkAttribute'
        db.delete_table(u'carnatic_workattribute')

        # Deleting model 'WorkAttributeType'
        db.delete_table(u'carnatic_workattributetype')

        # Deleting model 'WorkAttributeTypeValue'
        db.delete_table(u'carnatic_workattributetypevalue')

        # Deleting model 'Recording'
        db.delete_table(u'carnatic_recording')

        # Removing M2M table for field references on 'Recording'
        db.delete_table('carnatic_recording_references')

        # Deleting model 'InstrumentAlias'
        db.delete_table(u'carnatic_instrumentalias')

        # Deleting model 'Instrument'
        db.delete_table(u'carnatic_instrument')

        # Removing M2M table for field references on 'Instrument'
        db.delete_table('carnatic_instrument_references')

        # Deleting model 'InstrumentPerformance'
        db.delete_table(u'carnatic_instrumentperformance')

        # Deleting model 'Composer'
        db.delete_table(u'carnatic_composer')

        # Removing M2M table for field references on 'Composer'
        db.delete_table('carnatic_composer_references')

        # Deleting model 'Location'
        db.delete_table(u'carnatic_location')

        # Removing M2M table for field references on 'Location'
        db.delete_table('carnatic_location_references')


    models = {
        u'carnatic.artist': {
            'Meta': {'object_name': 'Artist'},
            'artist_type': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '1'}),
            'begin': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_instrument': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Instrument']", 'null': 'True', 'blank': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['data.Reference']", 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Source']", 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.GeographicRegion']", 'null': 'True', 'blank': 'True'})
        },
        u'carnatic.composer': {
            'Meta': {'object_name': 'Composer'},
            'begin': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['data.Reference']", 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Source']", 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.GeographicRegion']", 'null': 'True', 'blank': 'True'})
        },
        u'carnatic.concert': {
            'Meta': {'object_name': 'Concert'},
            'artists': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['carnatic.Artist']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Label']", 'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Location']", 'null': 'True', 'blank': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['data.Reference']", 'null': 'True', 'blank': 'True'}),
            'sabbah': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Sabbah']", 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Source']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tracks': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['carnatic.Recording']", 'symmetrical': 'False'}),
            'year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['data.Reference']", 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Source']", 'null': 'True', 'blank': 'True'})
        },
        u'carnatic.instrumentalias': {
            'Meta': {'object_name': 'InstrumentAlias'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instrument': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'to': u"orm['carnatic.Instrument']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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
        u'carnatic.location': {
            'Meta': {'object_name': 'Location'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'lng': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['data.Reference']", 'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Source']", 'null': 'True', 'blank': 'True'})
        },
        u'carnatic.musicalschool': {
            'Meta': {'object_name': 'MusicalSchool'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'carnatic.raaga': {
            'Meta': {'object_name': 'Raaga'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'carnatic.raagaalias': {
            'Meta': {'object_name': 'RaagaAlias'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'raaga': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'to': u"orm['carnatic.Raaga']"})
        },
        u'carnatic.recording': {
            'Meta': {'object_name': 'Recording'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'performance': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['carnatic.Artist']", 'through': u"orm['carnatic.InstrumentPerformance']", 'symmetrical': 'False'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['data.Reference']", 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Source']", 'null': 'True', 'blank': 'True'}),
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'raaga': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['carnatic.Raaga']", 'through': u"orm['carnatic.WorkRaaga']", 'symmetrical': 'False'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['data.Reference']", 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Source']", 'null': 'True', 'blank': 'True'}),
            'taala': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['carnatic.Taala']", 'through': u"orm['carnatic.WorkTaala']", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'carnatic.workattribute': {
            'Meta': {'object_name': 'WorkAttribute'},
            'attribute_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.WorkAttributeType']"}),
            'attribute_value': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.WorkAttributeTypeValue']", 'null': 'True', 'blank': 'True'}),
            'attribute_value_free': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Work']"})
        },
        u'carnatic.workattributetype': {
            'Meta': {'object_name': 'WorkAttributeType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'carnatic.workattributetypevalue': {
            'Meta': {'object_name': 'WorkAttributeTypeValue'},
            'attribute_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.WorkAttributeType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
        u'data.label': {
            'Meta': {'object_name': 'Label'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['data.Reference']", 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Source']", 'null': 'True', 'blank': 'True'})
        },
        u'data.reference': {
            'Meta': {'object_name': 'Reference'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'source_name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.SourceName']"}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'data.source': {
            'Meta': {'object_name': 'Source'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'source_name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.SourceName']"}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'data.sourcename': {
            'Meta': {'object_name': 'SourceName'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['carnatic']