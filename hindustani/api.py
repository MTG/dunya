# Copyright 2013,2014 Music Technology Group - Universitat Pompeu Fabra
#
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

from django.shortcuts import redirect
from rest_framework import generics
from rest_framework import serializers

from data import utils
from data.models import WithImageMixin
from dunya.api import get_collection_ids_from_request_or_error
from hindustani import models


class ArtistInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Artist
        fields = ['mbid', 'name']


class ComposerInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Composer
        fields = ['mbid', 'name']


class WorkInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Work
        fields = ['mbid', 'title']


class RecordingInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Recording
        fields = ['mbid', 'title']


class RaagInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Raag
        fields = ['uuid', 'common_name', 'name']


class TaalInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Taal
        fields = ['uuid', 'common_name', 'name']


class LayaInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Taal
        fields = ['uuid', 'common_name', 'name']


class FormInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Taal
        fields = ['uuid', 'common_name', 'name']


class ReleaseInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Release
        fields = ['mbid', 'title']


class InstrumentInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Instrument
        fields = ['mbid', 'name']


class TaalList(generics.ListAPIView):
    queryset = models.Taal.objects.all()
    serializer_class = TaalInnerSerializer


class TaalDetailSerializer(serializers.ModelSerializer):
    recordings = RecordingInnerSerializer(many=True, source='recording_set')
    composers = ComposerInnerSerializer(many=True)
    aliases = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = models.Taal
        fields = ['uuid', 'name', 'common_name', 'aliases', 'composers', 'recordings']


class TaalDetail(generics.RetrieveAPIView):
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'
    queryset = models.Taal.objects.all()
    serializer_class = TaalDetailSerializer


def taalbyid(request, pk):
    taal = models.Taal.objects.get(pk=pk)
    return redirect('api-hindustani-taal-detail', taal.uuid, permanent=True)


class RaagList(generics.ListAPIView):
    queryset = models.Raag.objects.all()
    serializer_class = RaagInnerSerializer


class RaagDetailSerializer(serializers.ModelSerializer):
    artists = ArtistInnerSerializer(many=True)
    recordings = RecordingInnerSerializer(many=True, source='recording_set')
    composers = ComposerInnerSerializer(many=True)
    aliases = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = models.Raag
        fields = ['uuid', 'name', 'common_name', 'aliases', 'artists', 'composers', 'recordings']


class RaagDetail(generics.RetrieveAPIView):
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'
    queryset = models.Raag.objects.all()
    serializer_class = RaagDetailSerializer


def raagbyid(request, pk):
    raag = models.Raag.objects.get(pk=pk)
    return redirect('api-hindustani-raag-detail', raag.uuid, permanent=True)


class LayaList(generics.ListAPIView):
    queryset = models.Laya.objects.all()
    serializer_class = LayaInnerSerializer


class LayaDetailSerializer(serializers.ModelSerializer):
    recordings = RecordingInnerSerializer(many=True)
    aliases = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = models.Laya
        fields = ['uuid', 'name', 'common_name', 'recordings', 'aliases']


class LayaDetail(generics.RetrieveAPIView):
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'
    queryset = models.Laya.objects.all()
    serializer_class = LayaDetailSerializer


def layabyid(request, pk):
    laya = models.Laya.objects.get(pk=pk)
    return redirect('api-hindustani-laya-detail', laya.uuid, permanent=True)


class FormList(generics.ListAPIView):
    queryset = models.Form.objects.all()
    serializer_class = FormInnerSerializer


class FormDetailSerializer(serializers.ModelSerializer):
    artists = ArtistInnerSerializer(many=True)
    recordings = RecordingInnerSerializer(many=True)
    aliases = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = models.Form
        fields = ['uuid', 'name', 'common_name', 'aliases', 'artists', 'recordings']


class FormDetail(generics.RetrieveAPIView):
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'
    queryset = models.Form.objects.all()
    serializer_class = FormDetailSerializer


def formbyid(request, pk):
    form = models.Form.objects.get(pk=pk)
    return redirect('api-hindustani-form-detail', form.uuid, permanent=True)


class InstrumentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Instrument
        fields = ['mbid', 'name']


class InstrumentList(generics.ListAPIView):
    queryset = models.Instrument.objects.all()
    serializer_class = InstrumentListSerializer


class InstrumentDetailSerializer(serializers.ModelSerializer):
    artists = ArtistInnerSerializer(many=True)

    class Meta:
        model = models.Instrument
        fields = ['mbid', 'name', 'artists']


class InstrumentDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    queryset = models.Instrument.objects.all()
    serializer_class = InstrumentDetailSerializer


class WorkListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Work
        fields = ['mbid', 'title']


class WorkList(generics.ListAPIView):
    queryset = models.Work.objects.all()
    serializer_class = WorkListSerializer


class WorkDetailSerializer(serializers.ModelSerializer):
    recordings = serializers.SerializerMethodField('recording_list')

    class Meta:
        model = models.Work
        fields = ['mbid', 'title', 'recordings']

    def recording_list(self, ob):
        collection_ids = get_collection_ids_from_request_or_error(self.context['request'])
        permission = utils.get_user_permissions(self.context['request'].user)
        recordings = ob.recording_set.with_permissions(collection_ids, permission)
        return RecordingInnerSerializer(recordings, many=True).data


class WorkDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    queryset = models.Work.objects.all()
    serializer_class = WorkDetailSerializer


class InstrumentPerformanceInnerSerializer(serializers.ModelSerializer):
    artist = ArtistInnerSerializer()
    instrument = InstrumentInnerSerializer()

    class Meta:
        model = models.InstrumentPerformance
        fields = ['artist', 'instrument', 'lead', 'attributes']


class RecordingList(generics.ListAPIView):
    def get_serializer_class(self):
        detail = self.request.GET.get('detail', None)
        if detail == '1':
            return RecordingDetailSerializer
        else:
            return RecordingInnerSerializer

    def get_queryset(self):
        collection_ids = get_collection_ids_from_request_or_error(self.request)
        permission = utils.get_user_permissions(self.request.user)
        return models.Recording.objects.with_permissions(collection_ids, permission).prefetch_related('raags', 'taals', 'layas', 'forms', 'works', 'instrumentperformance_set')


class RecordingDetailSerializer(serializers.ModelSerializer):
    release = serializers.SerializerMethodField('release_list')
    artists = InstrumentPerformanceInnerSerializer(source='instrumentperformance_set.all', many=True)
    raags = RaagInnerSerializer(many=True)
    taals = TaalInnerSerializer(many=True)
    layas = LayaInnerSerializer(many=True)
    forms = FormInnerSerializer(many=True)
    works = WorkInnerSerializer(many=True)
    album_artists = serializers.SerializerMethodField()

    class Meta:
        model = models.Recording
        fields = ['mbid', 'title', 'length', 'artists', 'raags', 'taals',
                  'layas', 'forms', 'works', 'release', 'album_artists']

    def release_list(self, ob):
        collection_ids = get_collection_ids_from_request_or_error(self.context['request'])
        permission = utils.get_user_permissions(self.context['request'].user)
        releases = ob.release_set.with_permissions(collection_ids, permission)
        rs = ReleaseInnerSerializer(releases, many=True)
        return rs.data

    def get_album_artists(self, ob):
        collection_ids = get_collection_ids_from_request_or_error(self.context['request'])
        permission = utils.get_user_permissions(self.context['request'].user)
        releases = ob.release_set.with_permissions(collection_ids, permission)
        ret = []
        if len(releases):
            ret = releases[0].artists
        arts = ArtistInnerSerializer(ret, many=True)
        return arts.data


class RecordingDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    queryset = models.Recording.objects.all()
    serializer_class = RecordingDetailSerializer


class ArtistListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Artist
        fields = ['mbid', 'name']


class ArtistList(generics.ListAPIView):
    queryset = models.Artist.objects.all()
    serializer_class = ArtistListSerializer


class ArtistDetailSerializer(serializers.ModelSerializer):
    releases = serializers.SerializerMethodField('release_list')
    instruments = InstrumentInnerSerializer(many=True)
    recordings = serializers.SerializerMethodField('recording_list')

    class Meta:
        model = models.Artist
        fields = ['mbid', 'name', 'releases', 'instruments', 'recordings']

    def release_list(self, ob):
        collection_ids = get_collection_ids_from_request_or_error(self.context['request'])
        permission = utils.get_user_permissions(self.context['request'].user)
        releases = ob.releases(collection_ids=collection_ids, permission=permission)
        cs = ReleaseInnerSerializer(releases, many=True)
        return cs.data

    def recording_list(self, ob):
        collection_ids = get_collection_ids_from_request_or_error(self.context['request'])
        permission = utils.get_user_permissions(self.context['request'].user)
        recordings = ob.recordings(collection_ids=collection_ids, permission=permission)
        rs = RecordingInnerSerializer(recordings, many=True)
        return rs.data


class ArtistDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    queryset = models.Artist.objects.all()
    serializer_class = ArtistDetailSerializer


class ReleaseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Release
        fields = ['mbid', 'title']


class ReleaseList(generics.ListAPIView):
    queryset = models.Release.objects.all()
    serializer_class = ReleaseListSerializer

    def get_queryset(self):
        collection_ids = get_collection_ids_from_request_or_error(self.request)
        permission = utils.get_user_permissions(self.request.user)
        return models.Release.objects.with_permissions(collection_ids, permission)


class ReleaseRecordingSerializer(serializers.ModelSerializer):
    mbid = serializers.ReadOnlyField(source='recording.mbid')
    title = serializers.ReadOnlyField(source='recording.title')

    class Meta:
        model = models.ReleaseRecording
        fields = ['mbid', 'title', 'disc', 'disctrack', 'track']


class ReleaseDetailSerializer(serializers.ModelSerializer, WithImageMixin):
    recordings = ReleaseRecordingSerializer(source='releaserecording_set', many=True)
    artists = serializers.SerializerMethodField('get_artists_and_instruments')
    release_artists = ArtistInnerSerializer(source='artists', many=True)
    image = serializers.SerializerMethodField('get_image_abs_url')

    class Meta:
        model = models.Release
        fields = ['mbid', 'title', 'year', 'image', 'recordings', 'artists', 'release_artists']

    def get_artists_and_instruments(self, ob):
        artists = ob.performers()
        data = []
        for a in artists:
            inner = ArtistInnerSerializer(a).data
            instrument = ob.instruments_for_artist(a)
            inner["instruments"] = InstrumentInnerSerializer(instrument, many=True).data
            data.append(inner)
        return data


class ReleaseDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    queryset = models.Release.objects.all()
    serializer_class = ReleaseDetailSerializer
