# Copyright 2018 Honglin Ma
# This file is part of Dunya
#
# Dunya is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation (FSF), either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/


from rest_framework import generics
from rest_framework import serializers

from data import utils
from data.models import WithImageMixin

from jingju import models

class ShengqiangBanshiInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ShengqiangBanshi
        fields = ['name']

class ScoreInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Score
        fields = ['name']

class PlayInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Play
        fields = ['title']

class RoleTypeInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RoleType
        fields = ['name', 'transliteration']

class InstrumentInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Artist
        fields = ['mbid', 'name']

class ArtistInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Artist
        fields = ['mbid', 'name', 'alias']

class RecordingInstrumentInnerSerializer(serializers.ModelSerializer):
    artist = ArtistInnerSerializer()
    instrument = InstrumentInnerSerializer()

    class Meta:
        model = models.RecordingInstrumentalist
        fields = ['artist', 'instrument']


class WorkInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Work
        fields = ['mbid', 'title']


class RecordingInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Recording
        fields = ['mbid', 'title']

class ReleaseInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Release
        fields = ['mbid', 'title']

class RecordingReleaseInnerSerializer(serializers.ModelSerializer):
    mbid = serializers.ReadOnlyField(source='recording.mbid')
    title = serializers.ReadOnlyField(source='recording.title')

    class Meta:
        model = models.RecordingRelease
        fields = ['mbid', 'title', 'disc', 'disctrack', 'track']

class ArtistDetailSerializer(serializers.ModelSerializer):
    role_type = RoleTypeInnerSerializer()
    instrument = InstrumentInnerSerializer()
    recordings = serializers.SerializerMethodField('recording_list')

    class Meta:
        model = models.Artist
        fields = ['mbid', 'name', 'alias', 'role_type', 'instrument', 'recordings']

    def recording_list(self, ob):
        collection_ids = self.context['request'].META.get('HTTP_DUNYA_COLLECTION', None)
        permission = utils.get_user_permissions(self.context['request'].user)
        recordings = ob.recording_set.with_permissions(collection_ids, permission)
        rs = RecordingInnerSerializer(recordings, many=True)
        return rs.data



class WorkDetailSerializer(serializers.ModelSerializer):
    score = ScoreInnerSerializer()
    play = PlayInnerSerializer()
    recordings = serializers.SerializerMethodField('recording_list')

    class Meta:
        model = models.Work
        fields = ['mbid', 'title', 'score', 'play', 'recordings']

    def recording_list(self, ob):
        collection_ids = self.context['request'].META.get('HTTP_DUNYA_COLLECTION', None)
        permission = utils.get_user_permissions(self.context['request'].user)
        recordings = ob.recording_set.with_permissions(collection_ids, permission)
        return RecordingInnerSerializer(recordings, many=True).data



class RecordingDetailSerializer(serializers.ModelSerializer):
    work = WorkInnerSerializer()
    performers = ArtistInnerSerializer(many=True)
    instrumentalists = RecordingInstrumentInnerSerializer(source='recordinginstrumentalist_set.all', many=True)
    release = serializers.SerializerMethodField('release_list')
    shengqiangbanshi = ShengqiangBanshiInnerSerializer(many=True)

    class Meta:
        model = models.Recording
        fields = ['mbid', 'title', 'release', 'work', 'performers', 'instrumentalists', 'shengqiangbanshi']

    def release_list(self, ob):
        collection_ids = self.context['request'].META.get('HTTP_DUNYA_COLLECTION', None)
        permission = utils.get_user_permissions(self.context['request'].user)
        release = ob.release_set.with_permissions(collection_ids, permission)
        cs = ReleaseInnerSerializer(release, many=True)
        return cs.data



class ReleaseDetailSerializer(serializers.ModelSerializer):
    # performer = ArtistInnerSerializer()
    artists = ArtistInnerSerializer(many=True)
    recordings = RecordingReleaseInnerSerializer(source='recordingrelease_set.all', many=True)

    class Meta:
        model = models.Release
        fields = ['mbid', 'title', 'recordings', 'artists']













class WorkList(generics.ListAPIView):
    queryset = models.Work.objects.all()
    serializer_class = WorkInnerSerializer

class WorkDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    queryset = models.Work.objects.all()
    serializer_class = WorkDetailSerializer

class RecordingList(generics.ListAPIView):
    serializer_class = RecordingInnerSerializer
    # queryset = models.Recording.objects.all()

    def get_queryset(self):
        collection_ids = self.request.META.get('HTTP_DUNYA_COLLECTION', None)
        permission = utils.get_user_permissions(self.request.user)
        return models.Recording.objects.with_permissions(collection_ids, permission)


class RecordingDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    # queryset = models.Recording.objects.all()
    serializer_class = RecordingDetailSerializer

    def get_queryset(self):
        collection_ids = self.request.META.get('HTTP_DUNYA_COLLECTION', None)
        permission = utils.get_user_permissions(self.request.user)
        return models.Recording.objects.with_permissions(collection_ids, permission)


class ReleaseList(generics.ListAPIView):
    serializer_class = ReleaseInnerSerializer
    # queryset = models.Release.objects.all()

    def get_queryset(self):
        collection_ids = self.request.META.get('HTTP_DUNYA_COLLECTION', None)
        permission = utils.get_user_permissions(self.request.user)
        return models.Release.objects.with_permissions(collection_ids, permission)


class ReleaseDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    # queryset = models.Release.objects.all()
    serializer_class = ReleaseDetailSerializer

    def get_queryset(self):
        permission = utils.get_user_permissions(self.request.user)
        return models.Release.objects.with_permissions(False, permission)

class ArtistList(generics.ListAPIView):
    serializer_class = ArtistInnerSerializer
    # queryset = models.Artist.objects.all()

    def get_queryset(self):
        collection_ids = self.request.META.get('HTTP_DUNYA_COLLECTION', None)
        permission = utils.get_user_permissions(self.request.user)
        return models.Artist.objects.with_permissions(collection_ids, permission)

class ArtistDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    # queryset = models.Artist.objects.all()
    serializer_class = ArtistDetailSerializer

    def get_queryset(self):
        collection_ids = self.request.META.get('HTTP_DUNYA_COLLECTION', None)
        permission = utils.get_user_permissions(self.request.user)
        return models.Artist.objects.with_permissions(collection_ids, permission)


class RoleTypeList(generics.ListAPIView):
    serializer_class = RoleTypeInnerSerializer
    queryset = models.RoleType.objects.all()