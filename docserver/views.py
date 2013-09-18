import json

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse

from docserver import models
from docserver import forms
from docserver import jobs
from docserver import serializers
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response

def index(request):
    return HttpResponse("Hello docserver")

class CollectionList(generics.ListAPIView):
    queryset = models.Collection.objects.all()
    serializer_class = serializers.CollectionListSerializer

class CollectionDetail(generics.RetrieveAPIView):
    lookup_field = 'slug'
    queryset = models.Collection.objects.all()
    serializer_class = serializers.CollectionDetailSerializer

class DocumentDetailExternal(generics.RetrieveAPIView):
    lookup_field='external_identifier'
    queryset = models.Document.objects.all()
    serializer_class = serializers.DocumentSerializer

class DocumentDetail(generics.RetrieveAPIView):
    lookup_field='pk'
    queryset = models.Document.objects.all()
    serializer_class = serializers.DocumentSerializer

def download_external(request, uuid, ftype):
    # TODO we could replace this with
    # https://github.com/MTG/freesound/blob/master/utils/nginxsendfile.py

    try:
        thetype = models.FileType.objects.get_by_extension(ftype)
    except models.FileType.DoesNotExist:
        thetype = None

    try:
        thedoc = models.Document.objects.get_by_external_id(uuid)
    except models.Document.DoesNotExist:
        thedoc = None

    if thedoc and thetype:
        # See if it's an extension
        files = thedoc.files.filter(file_type=thetype)
        if len(files) == 0:
            raise Http404
        else:
            fname = files[0].path
            contents = open(fname, 'rb').read()
        return HttpResponse(contents)
    elif thedoc and not thetype:
        # otherwise try derived type
        try:
            module = models.Module.objects.get(slug=ftype)
            qs = module.moduleversion_set
            # If there's a ?v= tag, use that version, otherwise get the latest
            version = request.GET.get("v")
            if version:
                qs = qs.filter(version=version)
            else:
                qs = qs.order_by("-date_added")
            if len(qs):
                return qs[0]
            else:
                # If no files, or none with this version
                raise Http404
        except models.Module.DoesNotExist:
            raise Http404
    else:
        # no extension or derived type
        raise Http404

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
            module = form.cleaned_data["module"]
            jobs.create_module(module)
            return HttpResponseRedirect(reverse('docserver-manager'))
    else:
        form = forms.ModuleForm()
    ret = {"form": form}
    return render(request, 'docserver/addmodule.html', ret)

def module(request):
    pass
