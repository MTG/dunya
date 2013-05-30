# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserProfile'
        db.create_table(u'social_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('birthday', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('avatar', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
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
            ('recording', models.ForeignKey(orm[u'carnatic.recording'], null=False))
        ))
        db.create_unique(u'social_playlist_recordings', ['playlist_id', 'recording_id'])

        # Adding model 'Tag'
        db.create_table(u'social_tag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal(u'social', ['Tag'])

        # Adding model 'ArtistTag'
        db.create_table(u'social_artisttag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.Tag'])),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Artist'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'social', ['ArtistTag'])

        # Adding unique constraint on 'ArtistTag', fields ['user', 'tag', 'artist']
        db.create_unique(u'social_artisttag', ['user_id', 'tag_id', 'artist_id'])

        # Adding model 'ConcertTag'
        db.create_table(u'social_concerttag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.Tag'])),
            ('concert', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Concert'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'social', ['ConcertTag'])

        # Adding unique constraint on 'ConcertTag', fields ['user', 'tag', 'concert']
        db.create_unique(u'social_concerttag', ['user_id', 'tag_id', 'concert_id'])

        # Adding model 'RecordingTag'
        db.create_table(u'social_recordingtag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.Tag'])),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Recording'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'social', ['RecordingTag'])

        # Adding unique constraint on 'RecordingTag', fields ['user', 'tag', 'recording']
        db.create_unique(u'social_recordingtag', ['user_id', 'tag_id', 'recording_id'])

        # Adding model 'WorkTag'
        db.create_table(u'social_worktag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.Tag'])),
            ('work', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Work'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'social', ['WorkTag'])

        # Adding unique constraint on 'WorkTag', fields ['user', 'tag', 'work']
        db.create_unique(u'social_worktag', ['user_id', 'tag_id', 'work_id'])

        # Adding model 'UserFollowsUser'
        db.create_table(u'social_userfollowsuser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_follower', self.gf('django.db.models.fields.related.ForeignKey')(related_name='follow_set', to=orm['auth.User'])),
            ('user_followed', self.gf('django.db.models.fields.related.ForeignKey')(related_name='to_follow_set', to=orm['auth.User'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'social', ['UserFollowsUser'])

        # Adding unique constraint on 'UserFollowsUser', fields ['user_follower', 'user_followed']
        db.create_unique(u'social_userfollowsuser', ['user_follower_id', 'user_followed_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'UserFollowsUser', fields ['user_follower', 'user_followed']
        db.delete_unique(u'social_userfollowsuser', ['user_follower_id', 'user_followed_id'])

        # Removing unique constraint on 'WorkTag', fields ['user', 'tag', 'work']
        db.delete_unique(u'social_worktag', ['user_id', 'tag_id', 'work_id'])

        # Removing unique constraint on 'RecordingTag', fields ['user', 'tag', 'recording']
        db.delete_unique(u'social_recordingtag', ['user_id', 'tag_id', 'recording_id'])

        # Removing unique constraint on 'ConcertTag', fields ['user', 'tag', 'concert']
        db.delete_unique(u'social_concerttag', ['user_id', 'tag_id', 'concert_id'])

        # Removing unique constraint on 'ArtistTag', fields ['user', 'tag', 'artist']
        db.delete_unique(u'social_artisttag', ['user_id', 'tag_id', 'artist_id'])

        # Deleting model 'UserProfile'
        db.delete_table(u'social_userprofile')

        # Deleting model 'Playlist'
        db.delete_table(u'social_playlist')

        # Removing M2M table for field recordings on 'Playlist'
        db.delete_table('social_playlist_recordings')

        # Deleting model 'Tag'
        db.delete_table(u'social_tag')

        # Deleting model 'ArtistTag'
        db.delete_table(u'social_artisttag')

        # Deleting model 'ConcertTag'
        db.delete_table(u'social_concerttag')

        # Deleting model 'RecordingTag'
        db.delete_table(u'social_recordingtag')

        # Deleting model 'WorkTag'
        db.delete_table(u'social_worktag')

        # Deleting model 'UserFollowsUser'
        db.delete_table(u'social_userfollowsuser')


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
            'sabbah': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Sabbah']", 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Source']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tracks': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['carnatic.Recording']", 'symmetrical': 'False'}),
            'year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
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
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Source']", 'null': 'True', 'blank': 'True'})
        },
        u'carnatic.instrumentperformance': {
            'Meta': {'object_name': 'InstrumentPerformance'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instrument': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Instrument']"}),
            'lead': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'performer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Artist']"}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Recording']"})
        },
        u'carnatic.location': {
            'Meta': {'object_name': 'Location'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'lng': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Source']", 'null': 'True', 'blank': 'True'})
        },
        u'carnatic.raaga': {
            'Meta': {'object_name': 'Raaga'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'carnatic.recording': {
            'Meta': {'object_name': 'Recording'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'performance': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['carnatic.Artist']", 'through': u"orm['carnatic.InstrumentPerformance']", 'symmetrical': 'False'}),
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
        u'carnatic.work': {
            'Meta': {'object_name': 'Work'},
            'composer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Composer']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'raaga': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['carnatic.Raaga']", 'through': u"orm['carnatic.WorkRaaga']", 'symmetrical': 'False'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Source']", 'null': 'True', 'blank': 'True'}),
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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'data.label': {
            'Meta': {'object_name': 'Label'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Source']", 'null': 'True', 'blank': 'True'})
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
        },
        u'social.artisttag': {
            'Meta': {'unique_together': "(('user', 'tag', 'artist'),)", 'object_name': 'ArtistTag'},
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Artist']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social.Tag']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'social.concerttag': {
            'Meta': {'unique_together': "(('user', 'tag', 'concert'),)", 'object_name': 'ConcertTag'},
            'concert': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Concert']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social.Tag']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'social.playlist': {
            'Meta': {'object_name': 'Playlist'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'recordings': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['carnatic.Recording']", 'symmetrical': 'False'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'social.recordingtag': {
            'Meta': {'unique_together': "(('user', 'tag', 'recording'),)", 'object_name': 'RecordingTag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Recording']"}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social.Tag']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'social.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        u'social.userfollowsuser': {
            'Meta': {'unique_together': "(('user_follower', 'user_followed'),)", 'object_name': 'UserFollowsUser'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'user_followed': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to_follow_set'", 'to': u"orm['auth.User']"}),
            'user_follower': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'follow_set'", 'to': u"orm['auth.User']"})
        },
        u'social.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'social.worktag': {
            'Meta': {'unique_together': "(('user', 'tag', 'work'),)", 'object_name': 'WorkTag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social.Tag']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Work']"})
        }
    }

    complete_apps = ['social']