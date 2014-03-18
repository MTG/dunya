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
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.urlresolvers import reverse

from django.core.servers.basehttp import FileWrapper
from django.conf import settings

from docserver import models
from docserver import forms
from docserver import jobs
from docserver import serializers
from docserver import util
from django.views.decorators.csrf import csrf_exempt

from rest_framework import authentication
from rest_framework import exceptions
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response

auther = authentication.TokenAuthentication()

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
    # Test authentication. We support a rest-framework token
    # or a logged-in user

    loggedin = request.user.is_authenticated()
    try:
        t = auther.authenticate(request)
        if t:
            token = True
        else:
            token = False
    except exceptions.AuthenticationFailed:
        token = False

    # The only thing that's limited at the moment is mp3 files
    if ftype == "mp3" and not (loggedin or token):
        return HttpResponse("Not logged in", status=401)

    # TODO we could replace or enhance this with
    # https://github.com/MTG/freesound/blob/master/utils/nginxsendfile.py
    try:
        version = request.GET.get("v")
        subtype = request.GET.get("subtype")
        part = request.GET.get("part")
        filepart = util._docserver_get_part(uuid, ftype, subtype, part, version)

        fname = filepart.fullpath

        contents = open(fname, 'rb').read()
        ctype = filepart.mimetype
        response = HttpResponse(contents, content_type=ctype)
        response['Content-Length'] = len(contents)
        return response
    except util.NoFileException:
        # TODO: Send a message with the 404 too, giving the reason
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

