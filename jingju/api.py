from rest_framework import generics
from rest_framework import serializers

from data import utils
from data.models import WithImageMixin

from jingju import models

class WorkInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Work
        fields = ['mbid', 'title']

class WorkList(generics.ListAPIView):
    queryset = models.Work.objects.all()
    serializer_class = WorkInnerSerializer

class RecordingInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Recording
        fields = ['mbid', 'title']

class RecordingList(generics.ListAPIView):
    serializer_class = RecordingInnerSerializer
    queryset = models.Recording.objects.all()
    # def get_queryset(self):
        # collection_ids = self.request.META.get('HTTP_DUNYA_COLLECTION', None)
        # permission = utils.get_user_permissions(self.request.user)
        # return models.Recording.objects.with_permissions(collection_ids, permission)