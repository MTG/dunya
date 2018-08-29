from rest_framework import generics
from rest_framework import serializers

from data import utils
from data.models import WithImageMixin

from jingju import models

class WorkInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Work
        fields = ['mbid', 'title']

class WorkDetailSerializer(serializers.ModelSerializer):
    score = ScoreInnerSerializer()
    play = PlayInnerSerializer()

    class Meta:
        model = models.Work
        fields = ['mbid', 'title', 'score', 'play']


class RecordingInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Recording
        fields = ['mbid', 'title']


class RecordingDetailSerializer(serializers.ModelSerializer):
    work = WorkInnerSerializer()
    performers = ArtistInnerSerializer(many=True)
    instrumentalists = RecordingInstrumentInnerSerializer(many=True)

    class Meta:
        model = models.Work
        fields = ['mbid', 'title', 'work', 'performers', 'instrumentalists']

class ReleaseInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Release
        fields = ['mbid', 'title']

class ReleaseDetailSerializer(serializers.ModelSerializer):
    performer = ArtistInnerSerializer()
    recordings = RecordingInnerSerializer(many=True)

    class Meta:
        model = models.Work
        fields = ['mbid', 'title', 'performer', 'recordings']


class ArtistInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Artist
        fields = ['mbid', 'name']

class ArtistDetailSerializer(serializers.ModelSerializer):
    role_type = RoleTypeInnerSerializer()
    instrument = InstrumentInnerSerializer()

    class Meta:
        model = models.Artist
        fields = ['mbid', 'title', 'role_type', 'instrument']

class InstrumentInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Artist
        fields = ['mbid', 'name']


class RecordingInstrumentInnerSerializer(serializers.ModelSerializer):
    artist = ArtistInnerSerializer()
    instrument = InstrumentInnerSerializer()

    class Meta:
        model = models.RecordingInstrumentalist
        fields = ['artist', 'instrument']

class RoleTypeInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RoleType
        fields = ['title']

class ScoreInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Score
        fields = ['title']

class PlayInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Play
        fields = ['title']


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
    queryset = models.Recording.objects.all()

class RecordingDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    queryset = models.Recording.objects.all()
    serializer_class = RecordingDetailSerializer


class ReleaseList(generics.ListAPIView):
    serializer_class = ReleaseInnerSerializer
    queryset = models.Release.objects.all()


class ReleaseDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    queryset = models.Release.objects.all()
    serializer_class = ReleaseDetailSerializer

class ArtistList(generics.ListAPIView):
    serializer_class = ArtistInnerSerializer
    queryset = models.Artist.objects.all()

class ArtistDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    queryset = models.Artist.objects.all()
    serializer_class = ArtistInnerSerializer


