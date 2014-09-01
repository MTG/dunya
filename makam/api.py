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

from makam import models

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

class FormInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Form
        fields = ['id', 'name']

class MakamInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Makam
        fields = ['id', 'name']

class ReleaseInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Release
        fields = ['mbid', 'title']

class InstrumentInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Instrument
        fields = ['id', 'name']

class MakamListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Makam
        fields = ['id', 'name']

class MakamList(generics.ListAPIView):
    queryset = models.Makam.objects.all()
    serializer_class = MakamListSerializer

class MakamDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Makam
        fields = ['id', 'name']

class MakamDetail(generics.RetrieveAPIView):
    lookup_field = 'pk'
    queryset = models.Makam.objects.all()
    serializer_class = MakamDetailSerializer


class FormListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Form
        fields = ['id', 'name']

class FormList(generics.ListAPIView):
    queryset = models.Form.objects.all()
    serializer_class = FormListSerializer

class FormDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Form
        fields = ['id', 'name']

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
    composer = ComposerInnerSerializer(source='composer')
    recordings = RecordingInnerSerializer(source='recording_set')

    class Meta:
        model = models.Work
        fields = ['mbid', 'title', 'composer', 'recordings']

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
    concert = ReleaseInnerSerializer(source='concert_set.get')
    artists = ArtistInnerSerializer(source='all_artists')
    work = RecordingInnerSerializer(source='work')

    class Meta:
        model = models.Recording
        fields = ['mbid', 'title', 'artists', 'work', 'concert']

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
    releases = ReleaseInnerSerializer(source='main_releases')
    instruments = InstrumentInnerSerializer(source='instruments')
    # recordings = RecordingInnerSerializer(source='recordings')

    class Meta:
        model = models.Artist
        fields = ['mbid', 'name', 'releases', 'instruments']

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
    recordings  = RecordingInnerSerializer(many=True)
    artists = ReleaseArtistSerializer(source='performers')
    release_artists = ArtistInnerSerializer(source='artists')

    class Meta:
        model = models.Release
        fields = ['mbid', 'title', 'recordings ', 'artists', 'release_artists']

class ReleaseDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    queryset = models.Release.objects.all()
    serializer_class = ReleaseDetailSerializer

