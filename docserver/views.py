import json

from django.http import HttpResponse, HttpResponseRedirect
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
    model = models.Document
    serializer = models.DocumentSerializer
    slug_field = 'docid'
    slug_url_kwarg = 'uuid'

def download(request, cslug, uuid, ftype):
    return HttpResponse("download %s from %s as %s" % (uuid, cslug, ftype))

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
