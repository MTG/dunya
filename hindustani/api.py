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

from hindustani import models

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

class RaagInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Raag
        fields = ['id', 'name']

class TaalInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Taal
        fields = ['id', 'name']

class LayaInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Taal
        fields = ['id', 'name']

class FormInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Taal
        fields = ['id', 'name']

class ReleaseInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Release
        fields = ['mbid', 'title']

class InstrumentInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Instrument
        fields = ['id', 'name']

class TaalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Taal
        fields = ['id', 'name']

class TaalList(generics.ListAPIView):
    queryset = models.Taal.objects.all()
    serializer_class = TaalListSerializer

class TaalDetailSerializer(serializers.ModelSerializer):
    recordings = RecordingInnerSerializer(source='recordings')
    composers = ComposerInnerSerializer(source='composers')
    aliases = serializers.RelatedField(many=True, source='aliases.all')

    class Meta:
        model = models.Taal
        fields = ['id', 'name', 'aliases', 'recordings', 'composers']

class TaalDetail(generics.RetrieveAPIView):
    lookup_field = 'pk'
    queryset = models.Taal.objects.all()
    serializer_class = TaalDetailSerializer

class RaagListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Raag
        fields = ['id', 'name']

class RaagList(generics.ListAPIView):
    queryset = models.Raag.objects.all()
    serializer_class = RaagListSerializer

class RaagDetailSerializer(serializers.ModelSerializer):
    artists = ArtistInnerSerializer(source='artists')
    recordings = WorkInnerSerializer(source='recordings')
    composers = ComposerInnerSerializer(source='composers')
    aliases = serializers.RelatedField(many=True, source='aliases.all')

    class Meta:
        model = models.Raag
        fields = ['id', 'name', 'aliases', 'artists', 'recordings', 'composers']

class RaagDetail(generics.RetrieveAPIView):
    lookup_field = 'pk'
    queryset = models.Raag.objects.all()
    serializer_class = RaagDetailSerializer

class LayaListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Laya
        fields = ['id', 'name']

class LayaList(generics.ListAPIView):
    queryset = models.Laya.objects.all()
    serializer_class = LayaListSerializer

class LayaDetailSerializer(serializers.ModelSerializer):
    recordings = WorkInnerSerializer(source='recordings')
    aliases = serializers.RelatedField(many=True, source='aliases.all')

    class Meta:
        model = models.Laya
        fields = ['id', 'name', 'recordings', 'aliases', ]

class LayaDetail(generics.RetrieveAPIView):
    lookup_field = 'pk'
    queryset = models.Laya.objects.all()
    serializer_class = LayaDetailSerializer

class FormListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Form
        fields = ['id', 'name']

class FormList(generics.ListAPIView):
    queryset = models.Form.objects.all()
    serializer_class = FormListSerializer

class FormDetailSerializer(serializers.ModelSerializer):
    artists = ArtistInnerSerializer(source='artists')
    recordings = WorkInnerSerializer(source='recordings')
    aliases = serializers.RelatedField(many=True, source='aliases.all')

    class Meta:
        model = models.Form
        fields = ['id', 'name', 'aliases', 'artists', 'recordings']

class FormDetail(generics.RetrieveAPIView):
    lookup_field = 'pk'
    queryset = models.Form.objects.all()
    serializer_class = FormDetailSerializer

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
    recordings = RecordingInnerSerializer(source='recording_set')

    class Meta:
        model = models.Work
        fields = ['mbid', 'title', 'recordings']

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
    release = ReleaseInnerSerializer(source='release_set.get')
    artists = ArtistInnerSerializer(source='all_artists')
    raags = RaagInnerSerializer(source='raags')
    taals = TaalInnerSerializer(source='taals')
    layas = LayaInnerSerializer(source='layas')
    forms = FormInnerSerializer(source='forms')
    works = WorkInnerSerializer(source='works')

    class Meta:
        model = models.Recording
        fields = ['mbid', 'title', 'artists', 'raags', 'taals', 'layas', 'forms', 'works', 'release']

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
    releases = ReleaseInnerSerializer(source='releases')
    instruments = InstrumentInnerSerializer(source='instruments')
    recordings = RecordingInnerSerializer(source='recordings')

    class Meta:
        model = models.Artist
        fields = ['mbid', 'name', 'releases', 'instruments', 'recordings']

class ArtistDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    queryset = models.Artist.objects.all()
    serializer_class = ArtistDetailSerializer


class ReleaseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Release
        fields = ['mbid', 'title']

class ReleaseList(generics.ListAPIView):
    queryset = models.Release.objects.all()
    serializer_class = ReleaseListSerializer

class ReleaseArtistSerializer(serializers.ModelSerializer):
    name = serializers.Field(source='performer.name')
    mbid = serializers.Field(source='performer.mbid')
    instrument = serializers.Field(source='instrument.name')

    class Meta:
        model = models.Artist
        fields = ['mbid', 'name', 'instrument']

class ReleaseDetailSerializer(serializers.ModelSerializer):
    tracks = RecordingInnerSerializer(many=True)
    artists = ReleaseArtistSerializer(source='performers')
    release_artists = ArtistInnerSerializer(source='artists')

    class Meta:
        model = models.Release
        fields = ['mbid', 'title', 'tracks', 'artists', 'release_artists']

class ReleaseDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    queryset = models.Release.objects.all()
    serializer_class = ReleaseDetailSerializer
