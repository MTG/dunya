import json

from django.http import HttpResponse
from django import shortcuts

from docserver import models
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response

def index(request):
    return HttpResponse("Hello docserver")

class CollectionList(generics.ListAPIView):
    model = models.Collection
    serializer_class = models.CollectionListSerializer

class CollectionDetail(generics.RetrieveAPIView):
    model = models.Collection
    serializer_class = models.CollectionDetailSerializer
    slug_field = 'slug'
    slug_url_kwarg = 'cslug'

class DocumentDetail(generics.RetrieveAPIView):
    model = models.Document
    serializer = models.DocumentSerializer
    slug_field = 'docid'
    slug_url_kwarg = 'uuid'

def download(request, cslug, uuid, ftype):
    return HttpResponse("download %s from %s as %s" % (uuid, cslug, ftype))
