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
import json

from rest_framework import generics
from rest_framework import serializers

from andalusian import models


class MusicalSchoolInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MusicalSchool
        fields = ['name', 'transliterated_name']


class ArtistInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Artist
        fields = ['mbid', 'name', 'transliterated_name']


class OrchestraInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Orchestra
        fields = ['mbid', 'name', 'transliterated_name']


class WorkInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Work
        fields = ['mbid', 'title', 'transliterated_title']


class AlbumInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Album
        fields = ['mbid', 'title', 'transliterated_title']


class GenreInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Genre
        fields = ['id', 'name', 'transliterated_name']


class RecordingInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Recording
        fields = ['mbid', 'title', 'transliterated_title']


class InstrumentInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Instrument
        fields = ['mbid', 'name']


class TabInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tab
        fields = ['uuid', 'name', 'transliterated_name', 'display_order']


class MizanInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Mizan
        fields = ['uuid', 'name', 'transliterated_name', 'display_order']


class NawbaInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Nawba
        fields = ['uuid', 'name', 'transliterated_name', 'display_order']


class FormInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Form
        fields = ['uuid', 'name', 'transliterated_name', 'display_order']


class SanaaInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sanaa
        fields = ['id', 'title', 'transliterated_title']


class PoemInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Poem
        fields = ['id', 'first_words', 'transliterated_first_words']


# =========== #

class MusicalSchoolDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MusicalSchool
        fields = ['id', 'name', 'transliterated_name']


class MusicalSchoolDetail(generics.RetrieveAPIView):
    lookup_field = 'pk'
    queryset = models.MusicalSchool.objects.all()
    serializer_class = MusicalSchoolDetailSerializer


class MusicalSchoolList(generics.ListAPIView):
    queryset = models.MusicalSchool.objects.all()
    serializer_class = MusicalSchoolInnerSerializer


class ArtistDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Artist
        fields = ['mbid', 'name', 'transliterated_name']


class ArtistDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    queryset = models.Artist.objects.all()
    serializer_class = ArtistDetailSerializer


class ArtistList(generics.ListAPIView):
    queryset = models.Artist.objects.all()
    serializer_class = ArtistInnerSerializer


class OrchestraDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Orchestra
        fields = ['mbid', 'name', 'transliterated_name']


class OrchestraDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    queryset = models.Orchestra.objects.all()
    serializer_class = OrchestraDetailSerializer


class OrchestraList(generics.ListAPIView):
    queryset = models.Orchestra.objects.all()
    serializer_class = OrchestraInnerSerializer


class WorkDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Work
        fields = ['mbid', 'title', 'transliterated_title']


class WorkDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    queryset = models.Work.objects.all()
    serializer_class = WorkDetailSerializer


class WorkList(generics.ListAPIView):
    queryset = models.Work.objects.all()
    serializer_class = WorkInnerSerializer


class AlbumDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Album
        fields = ['mbid', 'title', 'transliterated_title']


class AlbumDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    queryset = models.Album.objects.all()
    serializer_class = AlbumDetailSerializer


class AlbumList(generics.ListAPIView):
    queryset = models.Album.objects.all()
    serializer_class = AlbumInnerSerializer


class GenreDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Genre
        fields = ['id', 'name', 'transliterated_name']


class GenreDetail(generics.RetrieveAPIView):
    lookup_field = 'pk'
    queryset = models.Genre.objects.all()
    serializer_class = GenreDetailSerializer


class GenreList(generics.ListAPIView):
    queryset = models.Genre.objects.all()
    serializer_class = GenreInnerSerializer


class InstrumentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Instrument
        fields = ['mbid','name']


class InstrumentDetail(generics.RetrieveAPIView):
    lookup_field = 'pk'
    queryset = models.Instrument.objects.all()
    serializer_class = InstrumentDetailSerializer


class InstrumentList(generics.ListAPIView):
    queryset = models.Instrument.objects.all()
    serializer_class = InstrumentInnerSerializer


class TabDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tab
        fields = ['uuid', 'name', 'transliterated_name', 'display_order']


class TabDetail(generics.RetrieveAPIView):
    lookup_field = 'uuid'
    queryset = models.Tab.objects.all()
    serializer_class = TabDetailSerializer


class TabList(generics.ListAPIView):
    queryset = models.Tab.objects.all()
    serializer_class = TabInnerSerializer


class MizanDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Mizan
        fields = ['uuid', 'name', 'transliterated_name', 'display_order']


class MizanDetail(generics.RetrieveAPIView):
    lookup_field = 'uuid'
    queryset = models.Mizan.objects.all()
    serializer_class = MizanDetailSerializer


class MizanList(generics.ListAPIView):
    queryset = models.Mizan.objects.all()
    serializer_class = MizanInnerSerializer


class NawbaDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Nawba
        fields = ['uuid', 'name', 'transliterated_name', 'display_order']


class NawbaDetail(generics.RetrieveAPIView):
    lookup_field = 'uuid'
    queryset = models.Nawba.objects.all()
    serializer_class = NawbaDetailSerializer


class NawbaList(generics.ListAPIView):
    queryset = models.Nawba.objects.all()
    serializer_class = NawbaInnerSerializer


class FormDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Form
        fields = ['uuid', 'name', 'transliterated_name', 'display_order']


class FormDetail(generics.RetrieveAPIView):
    lookup_field = 'uuid'
    queryset = models.Form.objects.all()
    serializer_class = FormDetailSerializer


class FormList(generics.ListAPIView):
    queryset = models.Form.objects.all()
    serializer_class = FormInnerSerializer


class SectionDetailSerializer(serializers.ModelSerializer):
    tab = TabDetailSerializer()
    nawba = NawbaDetailSerializer()
    mizan = MizanDetailSerializer()
    form = FormDetailSerializer()
    
    class Meta:
        model = models.Section
        fields = ['start_time', 'end_time', 'tab', 'nawba', 'mizan', 'form']


class RecordingDetailSerializer(serializers.ModelSerializer):
    sections = SectionDetailSerializer(source='section_set.all', many=True)

    class Meta:
        model = models.Recording
        fields = ['mbid', 'title', 'transliterated_title', 'musescore_url', 'archive_url', 'sections']


class RecordingDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    queryset = models.Recording.objects.all()
    serializer_class = RecordingDetailSerializer


class RecordingList(generics.ListAPIView):
    queryset = models.Recording.objects.all()
    serializer_class = RecordingInnerSerializer


class SanaaDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sanaa
        fields = ['id', 'title', 'transliterated_title']


class SanaaDetail(generics.RetrieveAPIView):
    lookup_field = 'pk'
    queryset = models.Sanaa.objects.all()
    serializer_class = SanaaDetailSerializer


class SanaaList(generics.ListAPIView):
    queryset = models.Sanaa.objects.all()
    serializer_class = SanaaInnerSerializer


class PoemDetailSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField('get_text_obj')
    transliterated_text = serializers.SerializerMethodField('get_transliterated_text_obj')

    class Meta:
        model = models.Poem
        fields = ['text','transliterated_text','title', 'transliterated_title', 'first_words', 'transliterated_first_words']
    
    def get_text_obj(self, ob):
        text = json.loads(ob.text)
        return text
    
    def get_transliterated_text_obj(self, ob):
        text = json.loads(ob.transliterated_text)
        return text


class PoemDetail(generics.RetrieveAPIView):
    lookup_field = 'pk'
    queryset = models.Poem.objects.all()
    serializer_class = PoemDetailSerializer


class PoemList(generics.ListAPIView):
    queryset = models.Poem.objects.all()
    serializer_class = PoemInnerSerializer


class RecordingPoemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Poem
        fields = ['text', 'transliterated_text', 'title', 'transliterated_title', 'first_words',
                  'transliterated_first_words']


class LyricDetail(generics.ListAPIView):
    serializer_class = PoemDetailSerializer

    def get_queryset(self):
        mbid = self.kwargs['mbid'] 
        return models.Poem.objects.filter(recordingpoem__recording__mbid=mbid).order_by('recordingpoem__order_number').all()
