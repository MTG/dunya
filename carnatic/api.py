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
from rest_framework.generics import get_object_or_404

from carnatic import models
from data import utils
from data.models import WithImageMixin
from dunya.api import get_collection_ids_from_request_or_error


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


class RaagaInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Raaga
        fields = ['uuid', 'name', 'common_name']


class TaalaInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Taala
        fields = ['uuid', 'name', 'common_name']


class FormInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Form
        fields = ['name']


class ConcertInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Concert
        fields = ['mbid', 'title']


class InstrumentInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Instrument
        fields = ['mbid', 'name']


class InstrumentPerformanceInnerSerializer(serializers.ModelSerializer):
    artist = ArtistInnerSerializer()
    instrument = InstrumentInnerSerializer()

    class Meta:
        model = models.InstrumentPerformance
        fields = ['artist', 'instrument', 'lead', 'attributes']


class TaalaList(generics.ListAPIView):
    queryset = models.Taala.objects.all()
    serializer_class = TaalaInnerSerializer


class TaalaDetailSerializer(serializers.ModelSerializer):
    artists = ArtistInnerSerializer(many=True)
    works = WorkInnerSerializer(many=True)
    composers = ComposerInnerSerializer(many=True)
    aliases = serializers.StringRelatedField(many=True, read_only=True)
    recordings = serializers.SerializerMethodField('recording_list')

    class Meta:
        model = models.Taala
        fields = ['uuid', 'name', 'common_name', 'aliases', 'artists', 'works', 'composers', 'recordings']

    def recording_list(self, ob):
        form = self.context['request'].GET.get('form', None)
        recordings = ob.recordings_form(form)
        return RecordingInnerSerializer(recordings, many=True).data


class TaalaDetail(generics.RetrieveAPIView):
    lookup_field = 'uuid'
    queryset = models.Taala.objects.all()
    serializer_class = TaalaDetailSerializer


class RaagaList(generics.ListAPIView):
    queryset = models.Raaga.objects.all()
    serializer_class = RaagaInnerSerializer


class RaagaDetailSerializer(serializers.ModelSerializer):
    artists = ArtistInnerSerializer(many=True)
    works = WorkInnerSerializer(many=True)
    composers = ComposerInnerSerializer(many=True)
    aliases = serializers.StringRelatedField(many=True, read_only=True)
    recordings = serializers.SerializerMethodField('recording_list')

    class Meta:
        model = models.Raaga
        fields = ['uuid', 'name', 'common_name', 'aliases', 'artists', 'works', 'composers', 'recordings']

    def recording_list(self, ob):
        form = self.context['request'].GET.get('form', None)
        recordings = ob.recordings_form(form)
        return RecordingInnerSerializer(recordings, many=True).data


class RaagaDetail(generics.RetrieveAPIView):
    lookup_field = 'uuid'
    queryset = models.Raaga.objects.all()
    serializer_class = RaagaDetailSerializer


class InstrumentList(generics.ListAPIView):
    queryset = models.Instrument.objects.all()
    serializer_class = InstrumentInnerSerializer


class InstrumentDetailSerializer(serializers.ModelSerializer):
    artists = ArtistInnerSerializer(many=True)

    class Meta:
        model = models.Instrument
        fields = ['mbid', 'name', 'artists']


class InstrumentDetail(generics.RetrieveAPIView):
    lookup_field = 'pk'
    queryset = models.Instrument.objects.all()
    serializer_class = InstrumentDetailSerializer


class WorkList(generics.ListAPIView):
    queryset = models.Work.objects.all()
    serializer_class = WorkInnerSerializer


class WorkDetailSerializer(serializers.ModelSerializer):
    composers = ComposerInnerSerializer(many=True)
    raagas = RaagaInnerSerializer(source='raaga')
    taalas = TaalaInnerSerializer(source='taala')
    recordings = serializers.SerializerMethodField('recording_list')
    lyricists = ComposerInnerSerializer(many=True)

    class Meta:
        model = models.Work
        fields = ['mbid', 'title', 'composers', 'lyricists', 'raagas', 'taalas', 'recordings']

    def recording_list(self, ob):
        collection_ids = get_collection_ids_from_request_or_error(self.context['request'])
        permission = utils.get_user_permissions(self.context['request'].user)
        recordings = ob.recording_set.with_permissions(collection_ids, permission)
        return RecordingInnerSerializer(recordings, many=True).data


class WorkDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    queryset = models.Work.objects.all()

    def get_serializer_class(self):
        return WorkDetailSerializer


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
        return models.Recording.objects.with_permissions(collection_ids, permission).prefetch_related('works', 'forms', 'raagas', 'taalas', 'concert_set', 'instrumentperformance_set')


class RecordingDetailSerializer(serializers.ModelSerializer):
    concert = serializers.SerializerMethodField('concert_list')
    raaga = RaagaInnerSerializer(source='get_raaga', many=True)
    taala = TaalaInnerSerializer(source='get_taala', many=True)
    form = FormInnerSerializer(source='forms', many=True)
    work = WorkInnerSerializer(source='works', many=True)
    artists = InstrumentPerformanceInnerSerializer(source='instrumentperformance_set.all', many=True)
    album_artists = serializers.SerializerMethodField()

    class Meta:
        model = models.Recording
        fields = ['mbid', 'title', 'length', 'artists', 'raaga', 'taala', 'form', 'work', 'concert', 'album_artists']

    def concert_list(self, ob):
        collection_ids = get_collection_ids_from_request_or_error(self.context['request'])
        permission = utils.get_user_permissions(self.context['request'].user)
        concerts = ob.concert_set.with_permissions(collection_ids, permission)
        cs = ConcertInnerSerializer(concerts, many=True)
        return cs.data

    def get_album_artists(self, ob):
        collection_ids = get_collection_ids_from_request_or_error(self.context['request'])
        permission = utils.get_user_permissions(self.context['request'].user)
        concerts = ob.concert_set.with_permissions(collection_ids, permission)
        ret = []
        if len(concerts):
            ret = concerts[0].artists
        arts = ArtistInnerSerializer(ret, many=True)
        return arts.data


class RecordingDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    queryset = models.Recording.objects.all()
    serializer_class = RecordingDetailSerializer

    def get_queryset(self):
        collection_ids = get_collection_ids_from_request_or_error(self.request)
        permission = utils.get_user_permissions(self.request.user)
        return models.Recording.objects.with_permissions(collection_ids, permission)


class ArtistList(generics.ListAPIView):
    queryset = models.Artist.objects.all()
    serializer_class = ArtistInnerSerializer


class ArtistDetailSerializer(serializers.ModelSerializer):
    concerts = serializers.SerializerMethodField('concert_list')
    instruments = InstrumentInnerSerializer(many=True)
    recordings = serializers.SerializerMethodField('recording_list')

    class Meta:
        model = models.Artist
        fields = ['mbid', 'name', 'concerts', 'instruments', 'recordings']

    def concert_list(self, ob):
        collection_ids = get_collection_ids_from_request_or_error(self.context['request'])
        permission = utils.get_user_permissions(self.context['request'].user)
        concerts = ob.concerts(collection_ids=collection_ids, permission=permission)
        cs = ConcertInnerSerializer(concerts, many=True)
        return cs.data

    def recording_list(self, ob):
        collection_ids = get_collection_ids_from_request_or_error(self.context['request'])
        permission = utils.get_user_permissions(self.context['request'].user)
        recordings = ob.recordings(collection_ids, permission)
        rs = RecordingInnerSerializer(recordings, many=True)
        return rs.data


class ArtistDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    queryset = models.Artist.objects.all()

    def get_serializer_class(self):
        return ArtistDetailSerializer


class ConcertList(generics.ListAPIView):
    queryset = models.Concert.objects.all()
    serializer_class = ConcertInnerSerializer

    def get_queryset(self):
        collection_ids = get_collection_ids_from_request_or_error(self.request)
        permission = utils.get_user_permissions(self.request.user)
        return models.Concert.objects.with_permissions(collection_ids, permission)


class ConcertRecordingSerializer(serializers.ModelSerializer):
    mbid = serializers.ReadOnlyField(source='recording.mbid')
    title = serializers.ReadOnlyField(source='recording.title')

    class Meta:
        model = models.ConcertRecording
        fields = ['mbid', 'title', 'disc', 'disctrack', 'track']


class ConcertDetailSerializer(serializers.ModelSerializer, WithImageMixin):
    recordings = ConcertRecordingSerializer(source='concertrecording_set', many=True)
    artists = serializers.SerializerMethodField('get_artists_and_instruments')
    concert_artists = ArtistInnerSerializer(source='artists', many=True)
    image = serializers.SerializerMethodField('get_image_abs_url')

    class Meta:
        model = models.Concert
        fields = ['mbid', 'title', 'year', 'image', 'recordings', 'artists', 'concert_artists']

    def get_artists_and_instruments(self, ob):
        artists = ob.performers()
        data = []
        for a in artists:
            inner = ArtistInnerSerializer(a).data
            instrument = ob.instruments_for_artist(a)
            inner["instruments"] = InstrumentInnerSerializer(instrument, many=True).data
            data.append(inner)
        return data


class ConcertDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    serializer_class = ConcertDetailSerializer

    def get_queryset(self):
        # We only check if the user has access here - you do not
        # need to add the collection_id header if you specify the mbid
        # of a concert
        permission = utils.get_user_permissions(self.request.user)
        return models.Concert.objects.with_permissions([], permission)
