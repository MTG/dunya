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

class ReleaseRecordingInnerSerializer(serializers.ModelSerializer):
    mbid = serializers.ReadOnlyField(source='recording.mbid')
    title = serializers.ReadOnlyField(source='recording.title')
    class Meta:
        model = models.ReleaseRecording
        fields = ['mbid', 'title', 'track']

class RecordingInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Recording
        fields = ['mbid', 'title']

class FormInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Form
        fields = ['id', 'name']

class UsulInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Usul
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

class MakamList(generics.ListAPIView):
    queryset = models.Makam.objects.all()
    serializer_class = MakamInnerSerializer

class MakamDetailSerializer(serializers.ModelSerializer):
    works = WorkInnerSerializer(source='worklist', many=True)
    taksims = RecordingInnerSerializer(source='taksimlist', many=True)
    gazels = RecordingInnerSerializer(source='gazellist', many=True)

    class Meta:
        model = models.Makam
        fields = ['id', 'name', 'works', 'taksims', 'gazels']

class MakamDetail(generics.RetrieveAPIView):
    lookup_field = 'uuid'
    queryset = models.Makam.objects.all()
    serializer_class = MakamDetailSerializer

def makambyid(request, pk):
    makam = models.Makam.objects.get(pk=pk)
    return redirect('api-makam-makam-detail', makam.uuid, permanent=True)

class FormList(generics.ListAPIView):
    queryset = models.Form.objects.all()
    serializer_class = FormInnerSerializer

class FormDetailSerializer(serializers.ModelSerializer):
    works = WorkInnerSerializer(source='worklist', many=True)

    class Meta:
        model = models.Form
        fields = ['id', 'name', 'works']

class FormDetail(generics.RetrieveAPIView):
    lookup_field = 'uuid'
    queryset = models.Form.objects.all()
    serializer_class = FormDetailSerializer

def formbyid(request, pk):
    form = models.Form.objects.get(pk=pk)
    return redirect('api-makam-form-detail', form.uuid, permanent=True)

class UsulList(generics.ListAPIView):
    queryset = models.Usul.objects.all()
    serializer_class = UsulInnerSerializer

class UsulDetailSerializer(serializers.ModelSerializer):
    works = WorkInnerSerializer(source='worklist', many=True)
    taksims = RecordingInnerSerializer(source='taksimlist', many=True)
    gazels = RecordingInnerSerializer(source='gazellist', many=True)

    class Meta:
        model = models.Usul
        fields = ['id', 'name', 'works', 'taksims', 'gazels']

class UsulDetail(generics.RetrieveAPIView):
    lookup_field = 'uuid'
    queryset = models.Usul.objects.all()
    serializer_class = UsulDetailSerializer

def usulbyid(request, pk):
    usul = models.Usul.objects.get(pk=pk)
    return redirect('api-makam-usul-detail', usul.uuid, permanent=True)

class InstrumentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Instrument
        fields = ['id', 'name']

class InstrumentList(generics.ListAPIView):
    queryset = models.Instrument.objects.all()
    serializer_class = InstrumentListSerializer

class InstrumentDetailSerializer(serializers.ModelSerializer):
    artists = ArtistInnerSerializer(many=True)

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
    composers = ComposerInnerSerializer(source='composerlist', many=True)
    lyricists = ComposerInnerSerializer(source='lyricistlist', many=True)
    makams = MakamInnerSerializer(source='makamlist', many=True)
    forms = FormInnerSerializer(source='formlist', many=True)
    usuls = UsulInnerSerializer(source='usullist', many=True)
    recordings = serializers.SerializerMethodField('recording_list')

    class Meta:
        model = models.Work
        fields = ['mbid', 'title', 'composers', 'lyricists', 'makams', 'forms', 'usuls', 'recordings']

    def recording_list(self, ob):
        collection_ids = self.context['request'].META.get('HTTP_DUNYA_COLLECTION', None)
        permission = utils.get_user_permissions(self.context['request'].user)
        recordings = ob.recording_set.with_permissions(collection_ids, permission)
        return RecordingInnerSerializer(recordings, many=True).data

class WorkDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    queryset = models.Work.objects.all()
    serializer_class = WorkDetailSerializer


class RecordingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Recording
        fields = ['mbid', 'title']

class RecordingList(generics.ListAPIView):
    queryset = models.Recording.objects.all()
    serializer_class = RecordingListSerializer

    def get_queryset(self):
        collection_ids = self.request.META.get('HTTP_DUNYA_COLLECTION', None)
        permission = utils.get_user_permissions(self.request.user)
        return models.Recording.objects.with_permissions(collection_ids, permission)

class InstrumentPerformanceSerializer(serializers.ModelSerializer):
    instrument = InstrumentInnerSerializer()
    mbid = serializers.ReadOnlyField(source='artist.mbid')
    name = serializers.ReadOnlyField(source='artist.name')

    class Meta:
        model = models.InstrumentPerformance
        fields = ['mbid', 'name', 'instrument']

class RecordingDetailSerializer(serializers.ModelSerializer):
    releases = serializers.SerializerMethodField('release_list')
    performers = InstrumentPerformanceSerializer(source='instrumentperformance_set', many=True)
    works = WorkInnerSerializer(source='worklist', many=True)

    class Meta:
        model = models.Recording
        fields = ['mbid', 'title', 'releases', 'performers', 'works']

    def release_list(self, ob):
        collection_ids = self.context['request'].META.get('HTTP_DUNYA_COLLECTION', None)
        permission = utils.get_user_permissions(self.context['request'].user)
        releases = ob.release_set.with_permissions(collection_ids, permission)
        rs = ReleaseInnerSerializer(releases, many=True)
        return rs.data

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

    class Meta:
        model = models.Artist
        fields = ['mbid', 'name', 'releases', 'instruments']

    def release_list(self, ob):
        collection_ids = self.context['request'].META.get('HTTP_DUNYA_COLLECTION', None)
        permission = utils.get_user_permissions(self.context['request'].user)
        releases = ob.main_releases(collection_ids=collection_ids, permission=permission)
        cs = ReleaseInnerSerializer(releases, many=True)
        return cs.data

class ArtistDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    queryset = models.Artist.objects.all()
    serializer_class = ArtistDetailSerializer


class ComposerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Composer
        fields = ['mbid', 'name']

class ComposerList(generics.ListAPIView):
    queryset = models.Composer.objects.all()
    serializer_class = ComposerListSerializer

class ComposerDetailSerializer(serializers.ModelSerializer):
    works = WorkInnerSerializer(source='worklist', many=True)
    lyric_works = WorkInnerSerializer(source='lyricworklist', many=True)

    class Meta:
        model = models.Composer
        fields = ['mbid', 'name', 'works', 'lyric_works']

class ComposerDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    queryset = models.Composer.objects.all()
    serializer_class = ComposerDetailSerializer


class ReleaseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Release
        fields = ['mbid', 'title']

class ReleaseList(generics.ListAPIView):
    queryset = models.Release.objects.all()
    serializer_class = ReleaseListSerializer

    def get_queryset(self):
        collection_ids = self.request.META.get('HTTP_DUNYA_COLLECTION', None)
        permission = utils.get_user_permissions(self.request.user)
        return models.Release.objects.with_permissions(collection_ids, permission)

class ReleaseDetailSerializer(serializers.ModelSerializer, WithImageMixin):
    recordings  = ReleaseRecordingInnerSerializer(many=True, source='releaserecording_set')
    artists = ArtistInnerSerializer(source='performers', many=True)
    release_artists = ArtistInnerSerializer(source='artists', many=True)
    image = serializers.SerializerMethodField('get_image_abs_url')

    class Meta:
        model = models.Release
        fields = ['mbid', 'title', 'year', 'image', 'artists', 'release_artists', 'recordings']

class ReleaseDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    queryset = models.Release.objects.all()
    serializer_class = ReleaseDetailSerializer


class SymbtrListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SymbTr
        fields = ['uuid', 'name']

class SymbtrList(generics.ListAPIView):
    queryset = models.SymbTr.objects.all()
    serializer_class = SymbtrListSerializer

class SymbtrDetailSerializer(serializers.ModelSerializer, WithImageMixin):

    class Meta:
        model = models.SymbTr
        fields = ['uuid', 'name']

class SymbtrDetail(generics.RetrieveAPIView):
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'
    queryset = models.SymbTr.objects.all()
    serializer_class = SymbtrDetailSerializer

