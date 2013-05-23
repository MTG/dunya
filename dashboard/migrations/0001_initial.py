# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MusicbrainzCollection'
        db.create_table(u'dashboard_musicbrainzcollection', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'dashboard', ['MusicbrainzCollection'])

        # Adding model 'MusicbrainzRelease'
        db.create_table(u'dashboard_musicbrainzrelease', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.MusicbrainzCollection'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'dashboard', ['MusicbrainzRelease'])

        # Adding model 'MusicbrainzRecording'
        db.create_table(u'dashboard_musicbrainzrecording', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('release', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.MusicbrainzRelease'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('position', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'dashboard', ['MusicbrainzRecording'])

        # Adding model 'HealthMonitor'
        db.create_table(u'dashboard_healthmonitor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('pythonclass', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'dashboard', ['HealthMonitor'])

        # Adding model 'Status'
        db.create_table(u'dashboard_status', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.MusicbrainzRecording'])),
            ('monitor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.HealthMonitor'])),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal(u'dashboard', ['Status'])

        # Adding model 'LogMessage'
        db.create_table(u'dashboard_logmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.MusicbrainzRecording'])),
            ('monitor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.HealthMonitor'])),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'dashboard', ['LogMessage'])


    def backwards(self, orm):
        # Deleting model 'MusicbrainzCollection'
        db.delete_table(u'dashboard_musicbrainzcollection')

        # Deleting model 'MusicbrainzRelease'
        db.delete_table(u'dashboard_musicbrainzrelease')

        # Deleting model 'MusicbrainzRecording'
        db.delete_table(u'dashboard_musicbrainzrecording')

        # Deleting model 'HealthMonitor'
        db.delete_table(u'dashboard_healthmonitor')

        # Deleting model 'Status'
        db.delete_table(u'dashboard_status')

        # Deleting model 'LogMessage'
        db.delete_table(u'dashboard_logmessage')


    models = {
        u'dashboard.healthmonitor': {
            'Meta': {'object_name': 'HealthMonitor'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'pythonclass': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'dashboard.logmessage': {
            'Meta': {'object_name': 'LogMessage'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'monitor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.HealthMonitor']"}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.MusicbrainzRecording']"})
        },
        u'dashboard.musicbrainzcollection': {
            'Meta': {'object_name': 'MusicbrainzCollection'},
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'dashboard.musicbrainzrecording': {
            'Meta': {'object_name': 'MusicbrainzRecording'},
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'release': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.MusicbrainzRelease']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'dashboard.musicbrainzrelease': {
            'Meta': {'object_name': 'MusicbrainzRelease'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.MusicbrainzCollection']"}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'dashboard.status': {
            'Meta': {'object_name': 'Status'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monitor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.HealthMonitor']"}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.MusicbrainzRecording']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        }
    }

    complete_apps = ['dashboard']