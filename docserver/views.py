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

import json, os

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse

from django.core.servers.basehttp import FileWrapper
from django.conf import settings

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
        thetype = models.SourceFileType.objects.get_by_extension(ftype)
    except models.SourceFileType.DoesNotExist:
        thetype = None

    try:
        thedoc = models.Document.objects.get_by_external_id(uuid)
    except models.Document.DoesNotExist:
        thedoc = None

    if thedoc and thetype:
        # See if it's an extension
        files = thedoc.sourcefiles.filter(file_type=thetype)
        if len(files) == 0:
            raise Http404
        else:
            fname = files[0].path
            contents = open(fname, 'rb').read()
            response = HttpResponse(contents)
            response['Content-Length'] = len(contents)
            return response
    elif thedoc and not thetype:
        # otherwise try derived type
        try:
            module = models.Module.objects.get(slug=ftype)
            moduleversions = module.moduleversion_set
            # If there's a ?v= tag, use that version, otherwise get the latest
            version = request.GET.get("v")
            if version:
                moduleversions = moduleversions.filter(version=version)
            else:
                moduleversions = moduleversions.order_by("-date_added")

            if len(moduleversions):
                # filter by ?subtype
                # if a file has many subtypes and it's not set, then this is an error
                subtype = request.GET.get("subtype")
                dfs = None
                for mv in moduleversions:
                    # go through all the versions until we find a file of that version
                    dfs = thedoc.derivedfiles.filter(module_version=mv).all()
                    if subtype:
                        dfs = dfs.filter(outputname=subtype)
                    if dfs.count() > 0:
                        # We found some files, break
                        break
                if dfs.count() > 1:
                    return HttpResponse(status=400)
                elif dfs.count() == 1:
                    # Select the part.
                    # If the file has many parts and ?part is not set then it's an error
                    parts = dfs[0].parts
                    part = request.GET.get("part")
                    if part:
                        parts = parts.filter(part_order=int(part))
                    else:
                        parts = parts.all()
                    mimetype = dfs[0].mimetype
                    if parts.count() > 1:
                        return HttpResponse(status=400)
                    elif parts.count() == 1:
                        derived_root = settings.AUDIO_ROOT
                        file_path = parts[0].path
                        full_path = os.path.join(derived_root, file_path)
                        contents = open(full_path, 'rb').read()
                        return HttpResponse(contents, mimetype)
                    else:
                        raise Http404
                else:
                    # If no files, or none with this version
                    raise Http404
            else:
                # If no files, or none with this version
                raise Http404
        except models.Module.DoesNotExist:
            raise Http404
    else:
        # no extension or derived type
        raise Http404

#### Essentia manager

def is_staff(user):
    return user.is_staff

@user_passes_test(is_staff)
def manager(request):
    scan = request.GET.get("scan")
    if scan is not None:
        jobs.run_module(int(scan))
        return HttpResponseRedirect(reverse('docserver-manager'))
    update = request.GET.get("update")
    if update is not None:
        jobs.get_latest_module_version(int(update))
        return HttpResponseRedirect(reverse('docserver-manager'))

    essentias = models.EssentiaVersion.objects.all()
    modules = models.Module.objects.all()
    collections = models.Collection.objects.all()

    ret = {"essentias": essentias, "modules": modules, "collections": collections}
    return render(request, 'docserver/manager.html', ret)

@user_passes_test(is_staff)
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

@user_passes_test(is_staff)
def addmodule(request):
    if request.method == "POST":
        form = forms.ModuleForm(request.POST)
        if form.is_valid():
            module = form.cleaned_data["module"]
            collections = []
            for i in form.cleaned_data['collections']:
                collections.append(get_object_or_404(models.Collection, pk=int(i)))
            jobs.create_module(module, collections)
            return HttpResponseRedirect(reverse('docserver-manager'))
    else:
        form = forms.ModuleForm()
    ret = {"form": form}
    return render(request, 'docserver/addmodule.html', ret)

@user_passes_test(is_staff)
def collection(request, slug):
    collection = get_object_or_404(models.Collection, slug=slug)
    ret = {"collection": collection}
    return render(request, 'docserver/collection.html', ret)

@user_passes_test(is_staff)
def file(request, slug, uuid):
    collection = get_object_or_404(models.Collection, slug=slug)
    doc = collection.documents.get_by_external_id(uuid)
    ret = {"document": doc}
    return render(request, 'docserver/file.html', ret)

