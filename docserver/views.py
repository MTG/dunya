import json

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse

from docserver import models
from docserver import forms
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
    lookup_field='external_identifier'
    model = models.Document
    serializer_class = models.DocumentSerializer

def download(request, cslug, uuid, ftype):
    return HttpResponse("download %s from %s as %s" % (uuid, cslug, ftype))

def download_external(request, uuid, ftype):
    try:
        thetype = models.FileType.objects.get_by_extension(ftype)
    except models.FileType.DoesNotExist:
        raise Http404
    try:
        thedoc = models.Document.objects.get_by_external_id(uuid)
    except models.Document.DoesNotExist:
        raise Http404

    files = thedoc.files.filter(file_type=thetype)
    if len(files) == 0:
        raise Http404
    else:
        fname = files[0].path
        contents = open(fname).read()
    return HttpResponse(contents)


#### Essentia manager

def manager(request):
    essentias = models.EssentiaVersion.objects.all()
    modules = models.Module.objects.all()

    ret = {"essentias": essentias, "modules": modules}
    return render(request, 'docserver/manager.html', ret)

def addessentia(request):
    if request.method == "POST":
        form = forms.EssentiaVersionForm(request.POST)
        if form.is_valid():
            models.EssentiaVersion.objects.create(version=form.cleaned_data["version"], sha1=form.cleaned_data["sha1"])
            return HttpResponseRedirect(reverse('docserver-manager'))
    else:
        form = forms.EssentiaVersionForm()
    ret = {"form": form}
    return render(request, 'docserver/addessentia.html', ret)

def addmodule(request):
    if request.method == "POST":
        form = forms.ModuleForm(request.POST)
        if form.is_valid():
            models.Module.objects.create(name=form.cleaned_data["name"], path=form.cleaned_data["path"])
            return HttpResponseRedirect(reverse('docserver-manager'))
    else:
        form = forms.ModuleForm()
    ret = {"form": form}
    return render(request, 'docserver/addmodule.html', ret)

def module(request):
    pass
