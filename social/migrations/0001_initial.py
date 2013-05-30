# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Instrument'
        db.create_table(u'social_instrument', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'social', ['Instrument'])

        # Adding model 'Artist'
        db.create_table(u'social_artist', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('startdate', self.gf('django.db.models.fields.DateField')()),
            ('enddate', self.gf('django.db.models.fields.DateField')()),
            ('artist_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('main_instrument', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.Instrument'])),
        ))
        db.send_create_signal(u'social', ['Artist'])

        # Adding model 'Raaga'
        db.create_table(u'social_raaga', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal(u'social', ['Raaga'])

        # Adding model 'Taala'
        db.create_table(u'social_taala', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal(u'social', ['Taala'])

        # Adding model 'Work'
        db.create_table(u'social_work', (
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('raaga', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.Raaga'])),
            ('taala', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.Taala'])),
        ))
        db.send_create_signal(u'social', ['Work'])

        # Adding model 'Concert'
        db.create_table(u'social_concert', (
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('city', self.gf('django.db.models.fields.CharField')(default='unknown', max_length=100)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('quality', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal(u'social', ['Concert'])

        # Adding model 'Recording'
        db.create_table(u'social_recording', (
            ('work', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.Work'])),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('length', self.gf('django.db.models.fields.IntegerField')()),
            ('concert', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.Concert'])),
            ('raaga', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.Raaga'])),
            ('taala', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.Taala'])),
        ))
        db.send_create_signal(u'social', ['Recording'])

        # Adding model 'InstrumentPerformance'
        db.create_table(u'social_instrumentperformance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.Recording'])),
            ('instrument', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.Instrument'])),
            ('performer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.Artist'])),
        ))
        db.send_create_signal(u'social', ['InstrumentPerformance'])

        # Adding model 'UserProfile'
        db.create_table(u'social_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('birthday', self.gf('django.db.models.fields.DateField')()),
            ('avatar', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal(u'social', ['UserProfile'])

        # Adding model 'Playlist'
        db.create_table(u'social_playlist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('id_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'social', ['Playlist'])

        # Adding M2M table for field recordings on 'Playlist'
        db.create_table(u'social_playlist_recordings', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('playlist', models.ForeignKey(orm[u'social.playlist'], null=False)),
            ('recording', models.ForeignKey(orm[u'social.recording'], null=False))
        ))
        db.create_unique(u'social_playlist_recordings', ['playlist_id', 'recording_id'])

        # Adding model 'Comment'
        db.create_table(u'social_comment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('comment', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'social', ['Comment'])

        # Adding model 'Tag'
        db.create_table(u'social_tag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'social', ['Tag'])

        # Adding model 'ArtistTag'
        db.create_table(u'social_artisttag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.Tag'])),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.Artist'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'social', ['ArtistTag'])

        # Adding unique constraint on 'ArtistTag', fields ['user', 'tag', 'artist']
        db.create_unique(u'social_artisttag', ['user_id', 'tag_id', 'artist_id'])

        # Adding model 'ArtistComment'
        db.create_table(u'social_artistcomment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('comment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.Comment'])),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.Artist'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'social', ['ArtistComment'])

        # Adding unique constraint on 'ArtistComment', fields ['user', 'comment', 'artist']
        db.create_unique(u'social_artistcomment', ['user_id', 'comment_id', 'artist_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'ArtistComment', fields ['user', 'comment', 'artist']
        db.delete_unique(u'social_artistcomment', ['user_id', 'comment_id', 'artist_id'])

        # Removing unique constraint on 'ArtistTag', fields ['user', 'tag', 'artist']
        db.delete_unique(u'social_artisttag', ['user_id', 'tag_id', 'artist_id'])

        # Deleting model 'Instrument'
        db.delete_table(u'social_instrument')

        # Deleting model 'Artist'
        db.delete_table(u'social_artist')

        # Deleting model 'Raaga'
        db.delete_table(u'social_raaga')

        # Deleting model 'Taala'
        db.delete_table(u'social_taala')

        # Deleting model 'Work'
        db.delete_table(u'social_work')

        # Deleting model 'Concert'
        db.delete_table(u'social_concert')

        # Deleting model 'Recording'
        db.delete_table(u'social_recording')

        # Deleting model 'InstrumentPerformance'
        db.delete_table(u'social_instrumentperformance')

        # Deleting model 'UserProfile'
        db.delete_table(u'social_userprofile')

        # Deleting model 'Playlist'
        db.delete_table(u'social_playlist')

        # Removing M2M table for field recordings on 'Playlist'
        db.delete_table('social_playlist_recordings')

        # Deleting model 'Comment'
        db.delete_table(u'social_comment')

        # Deleting model 'Tag'
        db.delete_table(u'social_tag')

        # Deleting model 'ArtistTag'
        db.delete_table(u'social_artisttag')

        # Deleting model 'ArtistComment'
        db.delete_table(u'social_artistcomment')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'social.artist': {
            'Meta': {'object_name': 'Artist'},
            'artist_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'enddate': ('django.db.models.fields.DateField', [], {}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'main_instrument': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social.Instrument']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'startdate': ('django.db.models.fields.DateField', [], {}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'})
        },
        u'social.artistcomment': {
            'Meta': {'unique_together': "(('user', 'comment', 'artist'),)", 'object_name': 'ArtistComment'},
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social.Artist']"}),
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social.Comment']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'social.artisttag': {
            'Meta': {'unique_together': "(('user', 'tag', 'artist'),)", 'object_name': 'ArtistTag'},
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social.Artist']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social.Tag']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'social.comment': {
            'Meta': {'object_name': 'Comment'},
            'comment': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'social.concert': {
            'Meta': {'object_name': 'Concert'},
            'city': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '100'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'quality': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'social.instrument': {
            'Meta': {'object_name': 'Instrument'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'social.instrumentperformance': {
            'Meta': {'object_name': 'InstrumentPerformance'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instrument': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social.Instrument']"}),
            'performer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social.Artist']"}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social.Recording']"})
        },
        u'social.playlist': {
            'Meta': {'object_name': 'Playlist'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'recordings': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['social.Recording']", 'symmetrical': 'False'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'social.raaga': {
            'Meta': {'object_name': 'Raaga'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'social.recording': {
            'Meta': {'object_name': 'Recording'},
            'concert': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social.Concert']"}),
            'length': ('django.db.models.fields.IntegerField', [], {}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'raaga': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social.Raaga']"}),
            'taala': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social.Taala']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social.Work']"})
        },
        u'social.taala': {
            'Meta': {'object_name': 'Taala'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'social.tag': {
            'Meta': {'object_name': 'Tag'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'social.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'birthday': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'social.work': {
            'Meta': {'object_name': 'Work'},
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'raaga': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social.Raaga']"}),
            'taala': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social.Taala']"})
        }
    }

    complete_apps = ['social']