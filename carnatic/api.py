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

from rest_framework import generics
from rest_framework import serializers

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
        fields = ['id', 'name']

class TaalaInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Taala
        fields = ['id', 'name']

class ConcertInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Concert
        fields = ['mbid', 'title']

class InstrumentInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Instrument
        fields = ['id', 'name']

class TaalaListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Taala
        fields = ['id', 'name']

class TaalaList(generics.ListAPIView):
    queryset = models.Taala.objects.all()
    serializer_class = TaalaListSerializer

class TaalaDetailSerializer(serializers.ModelSerializer):
    artists = ArtistInnerSerializer(source='artists')
    works = WorkInnerSerializer(source='works')
    composers = ComposerInnerSerializer(source='composers')
    aliases = serializers.RelatedField(many=True, source='aliases.all')
    class Meta:
        model = models.Taala
        fields = ['id', 'name', 'transliteration', 'aliases', 'artists', 'works', 'composers']

class TaalaDetail(generics.RetrieveAPIView):
    lookup_field = 'pk'
    queryset = models.Taala.objects.all()
    serializer_class = TaalaDetailSerializer


class RaagaListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Raaga
        fields = ['id', 'name']

class RaagaList(generics.ListAPIView):
    queryset = models.Raaga.objects.all()
    serializer_class = RaagaListSerializer

class RaagaDetailSerializer(serializers.ModelSerializer):
    artists = ArtistInnerSerializer(source='artists')
    works = WorkInnerSerializer(source='works')
    composers = ComposerInnerSerializer(source='composers')
    aliases = serializers.RelatedField(many=True, source='aliases.all')
    class Meta:
        model = models.Raaga
        fields = ['id', 'name', 'transliteration', 'aliases', 'artists', 'works', 'composers']

class RaagaDetail(generics.RetrieveAPIView):
    lookup_field = 'pk'
    queryset = models.Raaga.objects.all()
    serializer_class = RaagaDetailSerializer


class InstrumentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Instrument
        fields = ['id', 'name']

class InstrumentList(generics.ListAPIView):
    queryset = models.Instrument.objects.all()
    serializer_class = InstrumentListSerializer

class InstrumentDetailSerializer(serializers.ModelSerializer):
    artists = ArtistInnerSerializer(source='artists')
    class Meta:
        model = models.Instrument
        fields = ['id', 'name', 'artists']

class InstrumentDetail(generics.RetrieveAPIView):
    lookup_field = 'pk'
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
    composer = ComposerInnerSerializer(source='composer')
    raagas = RaagaInnerSerializer(source='raaga')
    taalas = TaalaInnerSerializer(source='taala')
    recordings = RecordingInnerSerializer(source='recording_set')
    class Meta:
        model = models.Work
        fields = ['mbid', 'title', 'composer', 'raagas', 'taalas', 'recordings']

class WorkDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    queryset = models.Work.objects.all()
    serializer_class = WorkDetailSerializer


class RecordingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Recording
        fields = ['mbid', 'title']

class RecordingList(generics.ListAPIView):
    queryset = models.Recording.objects.all()
    serializer_class = RecordingListSerializer

class RecordingDetailSerializer(serializers.ModelSerializer):
    concert = ConcertInnerSerializer(source='concert_set.get')
    artists = ArtistInnerSerializer(source='all_artists')
    raaga = RaagaInnerSerializer(source='raaga')
    taala = TaalaInnerSerializer(source='taala')
    work = RecordingInnerSerializer(source='work')
    class Meta:
        model = models.Recording
        fields = ['mbid', 'title', 'artists', 'raaga', 'taala', 'work', 'concert']

class RecordingDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
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
    concerts = ConcertInnerSerializer(source='concerts')
    instruments = InstrumentInnerSerializer(source='instruments')
    recordings = RecordingInnerSerializer(source='recordings')
    class Meta:
        model = models.Artist
        fields = ['mbid', 'name', 'concerts', 'instruments', 'recordings']

class ArtistDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    queryset = models.Artist.objects.all()
    serializer_class = ArtistDetailSerializer


class ConcertListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Concert
        fields = ['mbid', 'title']

class ConcertList(generics.ListAPIView):
    queryset = models.Concert.objects.all()
    serializer_class = ConcertListSerializer

class ConcertArtistSerializer(serializers.ModelSerializer):
    name = serializers.Field(source='performer.name')
    mbid = serializers.Field(source='performer.mbid')
    instrument = serializers.Field(source='instrument.name')
    class Meta:
        model = models.Artist
        fields = ['mbid', 'name', 'instrument']

class ConcertDetailSerializer(serializers.ModelSerializer):
    tracks = RecordingInnerSerializer(many=True)
    artists = ConcertArtistSerializer(source='performers')
    concert_artists = ArtistInnerSerializer(source='artists')
    class Meta:
        model = models.Concert
        fields = ['mbid', 'title', 'tracks', 'artists', 'concert_artists']

class ConcertDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    queryset = models.Concert.objects.all()
    serializer_class = ConcertDetailSerializer


