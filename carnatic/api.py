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

from carnatic import models
from data.models import WithImageMixin 
from data import utils

from rest_framework import generics
from rest_framework import serializers
from django.shortcuts import redirect

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
        fields = ['uuid', 'name']

class TaalaInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Taala
        fields = ['uuid', 'name']

class ConcertInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Concert
        fields = ['mbid', 'title']

class InstrumentInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Instrument
        fields = ['id', 'name']


class WithBootlegAPIView(object):
    @property
    def with_bootlegs(self):
        is_staff = self.request.user.is_staff
        with_bootlegs = self.request.QUERY_PARAMS.get('with_bootlegs', None)
        with_bootlegs = with_bootlegs is not None and is_staff
        return with_bootlegs

    @property
    def is_staff(self):
        return self.request.user.is_staff


class TaalaList(generics.ListAPIView):
    queryset = models.Taala.objects.all()
    serializer_class = TaalaInnerSerializer

class TaalaDetailSerializer(serializers.ModelSerializer):
    artists = ArtistInnerSerializer(many=True)
    works = WorkInnerSerializer(many=True)
    composers = ComposerInnerSerializer(many=True)
    aliases = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = models.Taala
        fields = ['uuid', 'name', 'common_name', 'aliases', 'artists', 'works', 'composers']

class TaalaDetail(generics.RetrieveAPIView):
    lookup_field = 'uuid'
    queryset = models.Taala.objects.all()
    serializer_class = TaalaDetailSerializer

def taalabyid(request, pk):
    taala = models.Taala.objects.get(pk=pk)
    return redirect('api-carnatic-taala-detail', taala.uuid, permanent=True)

class RaagaList(generics.ListAPIView):
    queryset = models.Raaga.objects.all()
    serializer_class = RaagaInnerSerializer

class RaagaDetailSerializer(serializers.ModelSerializer):
    artists = ArtistInnerSerializer(many=True)
    works = WorkInnerSerializer(many=True)
    composers = ComposerInnerSerializer(many=True)
    aliases = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = models.Raaga
        fields = ['uuid', 'name', 'common_name', 'aliases', 'artists', 'works', 'composers']

class RaagaDetail(generics.RetrieveAPIView):
    lookup_field = 'uuid'
    queryset = models.Raaga.objects.all()
    serializer_class = RaagaDetailSerializer

def raagabyid(request, pk):
    raaga = models.Raaga.objects.get(pk=pk)
    return redirect('api-carnatic-raaga-detail', raaga.uuid, permanent=True)

class InstrumentList(generics.ListAPIView):
    queryset = models.Instrument.objects.all()
    serializer_class = InstrumentInnerSerializer

class InstrumentDetailSerializer(serializers.ModelSerializer):
    artists = ArtistInnerSerializer(many=True)

    class Meta:
        model = models.Instrument
        fields = ['id', 'name', 'artists']

class InstrumentDetail(generics.RetrieveAPIView):
    lookup_field = 'pk'
    queryset = models.Instrument.objects.all()
    serializer_class = InstrumentDetailSerializer


class WorkList(generics.ListAPIView):
    queryset = models.Work.objects.all()
    serializer_class = WorkInnerSerializer

class WorkDetailSerializer(serializers.ModelSerializer):
    composers = ComposerInnerSerializer()
    raagas = RaagaInnerSerializer(source='raaga', many=True)
    taalas = TaalaInnerSerializer(source='taala', many=True)
    recordings = serializers.SerializerMethodField('recording_list')

    class Meta:
        model = models.Work
        fields = ['mbid', 'title', 'composers', 'raagas', 'taalas', 'recordings']

    def recording_list(self, ob):
        collection_ids = self.context['request'].META.get('HTTP_DUNYA_COLLECTION', None)
        permission = utils.get_user_permissions(self.context['request'].user)
        recordings = ob.recording_set.get_from_collections(collection_ids, permission)
        return RecordingInnerSerializer(recordings, many=True).data

class BootlegWorkDetailSerializer(WorkDetailSerializer):
    with_bootlegs = True

class NoBootlegWorkDetailSerializer(WorkDetailSerializer):
    with_bootlegs = False

class WorkDetail(generics.RetrieveAPIView, WithBootlegAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    queryset = models.Work.objects.all()

    def get_serializer_class(self):
        if self.with_bootlegs:
            return BootlegWorkDetailSerializer
        else:
            return NoBootlegWorkDetailSerializer


class RecordingList(generics.ListAPIView, WithBootlegAPIView):
    serializer_class = RecordingInnerSerializer

    def get_queryset(self):
        return models.Recording.objects.with_bootlegs(self.with_bootlegs)


class RecordingDetailSerializer(serializers.ModelSerializer):
    concert = serializers.SerializerMethodField('concert_list')
    artists = ArtistInnerSerializer(source='all_artists', many=True)
    raaga = RaagaInnerSerializer()
    taala = TaalaInnerSerializer()
    work = WorkInnerSerializer()

    class Meta:
        model = models.Recording
        fields = ['mbid', 'title', 'artists', 'raaga', 'taala', 'work', 'concert']

    def concert_list(self, ob):
        collection_ids = self.context['request'].META.get('HTTP_DUNYA_COLLECTION', None)
        permission = utils.get_user_permissions(self.context['request'].user)
        concerts = ob.concert_set.get_from_collections(collection_ids, permission)
        cs = ConcertInnerSerializer(concerts, many=True)
        return cs.data


class RecordingDetail(generics.RetrieveAPIView, WithBootlegAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    queryset = models.Recording.objects.all()
    serializer_class = RecordingDetailSerializer

    def get_queryset(self):
        # We only check if the user is staff here - you do not
        # need to add ?with_bootlegs if you specify the mbid
        # of a bootleg recording
        return models.Recording.objects.with_bootlegs(self.is_staff)


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
        collection_ids = self.context['request'].META.get('HTTP_DUNYA_COLLECTION', None)
        permission = utils.get_user_permissions(self.context['request'].user)
        concerts = ob.concerts(collection_ids=collection_ids, permission=permission)
        cs = ConcertInnerSerializer(concerts, many=True)
        return cs.data

    def recording_list(self, ob):
        collection_ids = self.context['request'].META.get('HTTP_DUNYA_COLLECTION', None)
        permission = utils.get_user_permissions(self.context['request'].user)
        recordings = ob.recordings(collection_ids, permission)
        rs = RecordingInnerSerializer(recordings, many=True)
        return rs.data

class BootlegArtistDetailSerializer(ArtistDetailSerializer):
    with_bootlegs = True

class NoBootlegArtistDetailSerializer(ArtistDetailSerializer):
    with_bootlegs = False

class ArtistDetail(generics.RetrieveAPIView, WithBootlegAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    queryset = models.Artist.objects.all()

    def get_serializer_class(self):
        if self.with_bootlegs:
            return BootlegArtistDetailSerializer
        else:
            return NoBootlegArtistDetailSerializer


class ConcertList(generics.ListAPIView, WithBootlegAPIView):
    queryset = models.Concert.objects.all()
    serializer_class = ConcertInnerSerializer

    def get_queryset(self):
        collection_ids = self.request.META.get('HTTP_DUNYA_COLLECTION', None)
        permission = utils.get_user_permissions(self.request.user)
        return models.Concert.objects.get_from_collections(collection_ids, permission)

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


class ConcertDetail(generics.RetrieveAPIView, WithBootlegAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    serializer_class = ConcertDetailSerializer

    def get_queryset(self):
        # We only check if the user has access here - you do not
        # need to add the collection_id header if you specify the mbid
        # of a concert
        permission = utils.get_user_permissions(self.request.user)
        return models.Concert.objects.with_permissions(permission)
