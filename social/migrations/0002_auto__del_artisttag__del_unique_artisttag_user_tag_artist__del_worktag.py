# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'RecordingTag', fields ['user', 'tag', 'recording']
        db.delete_unique(u'social_recordingtag', ['user_id', 'tag_id', 'recording_id'])

        # Removing unique constraint on 'ConcertTag', fields ['user', 'tag', 'concert']
        db.delete_unique(u'social_concerttag', ['user_id', 'tag_id', 'concert_id'])

        # Removing unique constraint on 'WorkTag', fields ['user', 'tag', 'work']
        db.delete_unique(u'social_worktag', ['user_id', 'tag_id', 'work_id'])

        # Removing unique constraint on 'ArtistTag', fields ['user', 'tag', 'artist']
        db.delete_unique(u'social_artisttag', ['user_id', 'tag_id', 'artist_id'])

        # Deleting model 'ArtistTag'
        db.delete_table(u'social_artisttag')

        # Deleting model 'WorkTag'
        db.delete_table(u'social_worktag')

        # Deleting model 'ConcertTag'
        db.delete_table(u'social_concerttag')

        # Deleting model 'RecordingTag'
        db.delete_table(u'social_recordingtag')

        # Adding model 'Annotation'
        db.create_table(u'social_annotation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.Tag'])),
            ('entity_id', self.gf('django.db.models.fields.IntegerField')()),
            ('entity_type', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal(u'social', ['Annotation'])

        # Adding unique constraint on 'Annotation', fields ['user', 'tag', 'entity_id', 'entity_type']
        db.create_unique(u'social_annotation', ['user_id', 'tag_id', 'entity_id', 'entity_type'])


    def backwards(self, orm):
        # Removing unique constraint on 'Annotation', fields ['user', 'tag', 'entity_id', 'entity_type']
        db.delete_unique(u'social_annotation', ['user_id', 'tag_id', 'entity_id', 'entity_type'])

        # Adding model 'ArtistTag'
        db.create_table(u'social_artisttag', (
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Artist'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.Tag'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'social', ['ArtistTag'])

        # Adding unique constraint on 'ArtistTag', fields ['user', 'tag', 'artist']
        db.create_unique(u'social_artisttag', ['user_id', 'tag_id', 'artist_id'])

        # Adding model 'WorkTag'
        db.create_table(u'social_worktag', (
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('work', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Work'])),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.Tag'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'social', ['WorkTag'])

        # Adding unique constraint on 'WorkTag', fields ['user', 'tag', 'work']
        db.create_unique(u'social_worktag', ['user_id', 'tag_id', 'work_id'])

        # Adding model 'ConcertTag'
        db.create_table(u'social_concerttag', (
            ('concert', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Concert'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.Tag'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'social', ['ConcertTag'])

        # Adding unique constraint on 'ConcertTag', fields ['user', 'tag', 'concert']
        db.create_unique(u'social_concerttag', ['user_id', 'tag_id', 'concert_id'])

        # Adding model 'RecordingTag'
        db.create_table(u'social_recordingtag', (
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.Tag'])),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['carnatic.Recording'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'social', ['RecordingTag'])

        # Adding unique constraint on 'RecordingTag', fields ['user', 'tag', 'recording']
        db.create_unique(u'social_recordingtag', ['user_id', 'tag_id', 'recording_id'])

        # Deleting model 'Annotation'
        db.delete_table(u'social_annotation')


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
            'description': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Description']", 'null': 'True', 'blank': 'True'}),
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
            'description': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Description']", 'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['data.Reference']", 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Source']", 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.GeographicRegion']", 'null': 'True', 'blank': 'True'})
        },
        u'carnatic.geographicregion': {
            'Meta': {'object_name': 'GeographicRegion'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'carnatic.instrument': {
            'Meta': {'object_name': 'Instrument'},
            'description': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Description']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['data.Reference']", 'null': 'True', 'blank': 'True'}),
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
        u'carnatic.raaga': {
            'Meta': {'object_name': 'Raaga'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'carnatic.recording': {
            'Meta': {'object_name': 'Recording'},
            'description': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Description']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'performance': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['carnatic.Artist']", 'through': u"orm['carnatic.InstrumentPerformance']", 'symmetrical': 'False'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['data.Reference']", 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Source']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Work']", 'null': 'True', 'blank': 'True'})
        },
        u'carnatic.taala': {
            'Meta': {'object_name': 'Taala'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'carnatic.work': {
            'Meta': {'object_name': 'Work'},
            'composer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['carnatic.Composer']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Description']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'raaga': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['carnatic.Raaga']", 'through': u"orm['carnatic.WorkRaaga']", 'symmetrical': 'False'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['data.Reference']", 'null': 'True', 'blank': 'True'}),
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
        u'data.description': {
            'Meta': {'object_name': 'Description'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
        },
        u'social.annotation': {
            'Meta': {'unique_together': "(('user', 'tag', 'entity_id', 'entity_type'),)", 'object_name': 'Annotation'},
            'entity_id': ('django.db.models.fields.IntegerField', [], {}),
            'entity_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social.Tag']"}),
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
        }
    }

    complete_apps = ['social']