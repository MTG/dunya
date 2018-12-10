from rest_framework import generics
from rest_framework import serializers

from data import utils
from dunya.api import get_collection_ids_from_request_or_error

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
        fields = ['uuid', 'code', 'name', 'romanisation']


class InstrumentInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Artist
        fields = ['mbid', 'name']


class ArtistInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Artist
        fields = ['mbid', 'name', 'romanisation']


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
        fields = ['mbid', 'name', 'romanisation', 'role_type', 'instrument', 'recordings']

    def recording_list(self, ob):
        collection_ids = get_collection_ids_from_request_or_error(self.context['request'])
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
        collection_ids = get_collection_ids_from_request_or_error(self.context['request'])
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
        collection_ids = get_collection_ids_from_request_or_error(self.context['request'])
        permission = utils.get_user_permissions(self.context['request'].user)
        release = ob.release_set.with_permissions(collection_ids, permission)
        cs = ReleaseInnerSerializer(release, many=True)
        return cs.data


class ReleaseDetailSerializer(serializers.ModelSerializer):
    artists = ArtistInnerSerializer(many=True)
    recordings = RecordingReleaseInnerSerializer(source='recordingrelease_set.all', many=True)

    class Meta:
        model = models.Release
        fields = ['mbid', 'title', 'recordings', 'artists']


class RoleTypeDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.RoleType
        fields = ['code', 'name', 'romanisation']


class WorkList(generics.ListAPIView):
    queryset = models.Work.objects.all()
    serializer_class = WorkInnerSerializer


class WorkDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    queryset = models.Work.objects.all()
    serializer_class = WorkDetailSerializer


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
        return models.Recording.objects.with_permissions(collection_ids, permission).select_related('work').prefetch_related('recordinginstrumentalist_set__artist', 'recordinginstrumentalist_set__instrument', 'performers', 'shengqiangbanshi')


class RecordingDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    serializer_class = RecordingDetailSerializer

    def get_queryset(self):
        collection_ids = get_collection_ids_from_request_or_error(self.request)
        permission = utils.get_user_permissions(self.request.user)
        return models.Recording.objects.with_permissions(collection_ids, permission)


class ReleaseList(generics.ListAPIView):
    serializer_class = ReleaseInnerSerializer

    def get_queryset(self):
        collection_ids = get_collection_ids_from_request_or_error(self.request)
        permission = utils.get_user_permissions(self.request.user)
        return models.Release.objects.with_permissions(collection_ids, permission)


class ReleaseDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    serializer_class = ReleaseDetailSerializer

    def get_queryset(self):
        permission = utils.get_user_permissions(self.request.user)
        return models.Release.objects.with_permissions(None, permission)


class ArtistList(generics.ListAPIView):
    def get_serializer_class(self):
        detail = self.request.GET.get('detail', None)
        if detail == '1':
            return ArtistDetailSerializer
        else:
            return ArtistInnerSerializer

    def get_queryset(self):
        collection_ids = get_collection_ids_from_request_or_error(self.request)
        permission = utils.get_user_permissions(self.request.user)
        return models.Artist.objects.with_permissions(collection_ids, permission).select_related('role_type', 'instrument')


class ArtistDetail(generics.RetrieveAPIView):
    lookup_field = 'mbid'
    lookup_url_kwarg = 'uuid'
    serializer_class = ArtistDetailSerializer

    def get_queryset(self):
        collection_ids = get_collection_ids_from_request_or_error(self.request)
        permission = utils.get_user_permissions(self.request.user)
        return models.Artist.objects.with_permissions(collection_ids, permission)


class RoleTypeList(generics.ListAPIView):
    serializer_class = RoleTypeInnerSerializer
    queryset = models.RoleType.objects.all()


class RoleTypeDetail(generics.RetrieveAPIView):
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'

    serializer_class = RoleTypeDetailSerializer
    queryset = models.RoleType.objects.all()
