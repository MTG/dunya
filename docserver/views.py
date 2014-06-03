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
import collections
import datetime

from django.http import HttpResponse
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.urlresolvers import reverse
from django.core.servers.basehttp import FileWrapper
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from docserver import models
from docserver import forms
from docserver import jobs
from docserver import serializers
from docserver import util
from dunya.celery import app
import dashboard

from rest_framework import authentication
from rest_framework import exceptions
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response

from sendfile import sendfile

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
    is_staff = request.user.is_staff
    try:
        t = auther.authenticate(request)
        if t:
            is_staff = t[0].is_staff
            token = True
        else:
            token = False
    except exceptions.AuthenticationFailed:
        token = False

    referrer = request.META.get("HTTP_REFERER")
    good_referrer = False
    if referrer and "dunya.compmusic.upf.edu" in referrer:
        good_referrer = True

    # The only thing that's limited at the moment is mp3 files
    if ftype == "mp3" and not (loggedin or token or good_referrer):
        return HttpResponse("Not logged in", status=401)

    try:
        version = request.GET.get("v")
        subtype = request.GET.get("subtype")
        part = request.GET.get("part")
        filepart = util._docserver_get_part(uuid, ftype, subtype, part, version)

        fname = filepart.fullpath
        mimetype = filepart.mimetype

        ratelimit = "off"
        if ftype == "mp3" and not is_staff:
            # 200k
            ratelimit = 200*1024

        # TODO: We should ratelimit mp3 requests, but not any others,
        # so we need a different path for nginx for these ones
        response = sendfile(request, fname, mimetype=mimetype)
        response['X-Accel-Limit-Rate'] = ratelimit

        return response
    except util.TooManyFilesException as e:
        r = ""
        if e.args:
            r = e.args[0]
        return HttpResponseBadRequest(e)
    except util.NoFileException as e:
        r = ""
        if e.args:
            r = e.args[0]
        return HttpResponseNotFound(e)

#### Essentia manager

def is_staff(user):
    return user.is_staff

@user_passes_test(is_staff)
def manager(request):
    scan = request.GET.get("scan")
    if scan is not None:
        jobs.run_module(int(scan))
        return redirect('docserver-manager')
    update = request.GET.get("update")
    if update is not None:
        jobs.get_latest_module_version(int(update))
        return redirect('docserver-manager')
    register = request.GET.get("register")
    if register is not None:
        jobs.register_host.apply_async([register], queue=register)
        return redirect('docserver-manager')
    if request.method == "POST":
        update = request.POST.get("updateall")
        if update is not None:
            jobs.update_all_workers()
            return redirect('docserver-manager')

    modules = models.Module.objects.all()
    collections = models.Collection.objects.all()

    inspect = app.control.inspect()
    # TODO: Load the task data via ajax, so the page loads quickly
    hosts = inspect.active()
    workerobs = models.Worker.objects.all()
    workerkeys = ["celery@%s" % w.hostname for w in workerobs]
    if hosts:
        hostkeys = hosts.keys()
        workers = list(set(workerkeys) & set(hostkeys))
        neww = []
        for w in workers:
            host = w.split("@")[1] 
            theworker = workerobs.get(hostname=host)
            num_proc = len(hosts[w])
            if theworker.state == models.Worker.UPDATING:
                state = "Updating"
            elif num_proc:
                state = "Active"
            else:
                state = "Idle"
            neww.append({"host": host,
                         "number": num_proc,
                         "state": state,
                         "worker": theworker})

        workers = neww
        newworkers = list(set(hostkeys) - set(workerkeys))
        newworkers = [w.split("@")[1] for w in newworkers]
        inactiveworkers = list(set(workerkeys) - set(hostkeys))
        inactiveworkers = [w.split("@")[1] for w in inactiveworkers]
    else:
        workers = []
        newworkers = []
        inactiveworkers = [w.split("@")[1] for w in workerkeys]

    latestpycm = models.PyCompmusicVersion.objects.order_by('-commit_date').first()
    latestessentia = models.EssentiaVersion.objects.order_by('-commit_date').first()

    ret = {"modules": modules, "collections": collections, "workers": workers,\
            "newworkers": newworkers, "inactiveworkers": inactiveworkers,
            "latestpycm": latestpycm, "latestessentia": latestessentia}
    return render(request, 'docserver/manager.html', ret)

def understand_task(task):
    tname = task["name"]
    try:
        args = json.loads(task["args"])
    except ValueError:
        args = []
    thetask = {"name": tname}
    # Magic task splitter
    if tname == "dashboard.jobs.load_musicbrainz_collection":
        thetask["type"] = "loadcollection"
        thetask["nicename"] = "Import musicbrainz collection"
        collectionid = args[0]
        coll = dashboard.models.Collection.objects.get(pk=collectionid)
        thetask["collection"] = coll
    elif tname == "dashboard.jobs.import_all_releases" or tname == "dashboard.jobs.force_import_all_releases":
        thetask["type"] = "importreleases"
        thetask["nicename"] = "Import releases in collection"
        collectionid = args[0]
        coll = dashboard.models.Collection.objects.get(pk=collectionid)
        thetask["collection"] = coll
    elif tname == "dashboard.jobs.import_single_release":
        thetask["type"] = ""
        thetask["nicename"] = ""
    elif tname == "docserver.jobs.update_essentia":
        thetask["type"] = "essentia"
        thetask["nicename"] = "Updating essentia"
    elif tname == "docserver.jobs.update_pycompmusic":
        thetask["type"] = ""
        thetask["nicename"] = ""
    elif tname == "docserver.jobs.process_document":
        thetask["type"] = "process"
        thetask["nicename"] = "Running extractor"

        documentid = args[0]
        moduleversionid = args[1]
        version = models.ModuleVersion.objects.get(pk=moduleversionid)
        document = models.Document.objects.get(pk=documentid)
        thetask["moduleversion"] = version
        thetask["document"] = document
    return thetask

@user_passes_test(is_staff)
def worker(request, hostname):
    # TODO: Show logs/stdout

    # TODO: Load the task data via ajax, so the page loads quickly

    # TODO: Can we use a redis queue to show the last 5 things that went
    #       through this server? We'll have a moduleversion, so can show
    #       the derived files too. Make it expire after 10 minutes
    # TODO: We need logging when someone performs an action.
    # Need to know and when (incase it goes bad)

    updatee = request.GET.get("updateessentia")
    if updatee is not None:
        jobs.update_essentia.apply_async([hostname], queue=hostname)
        return redirect('docserver-worker', hostname)
    updatep = request.GET.get("updatepcm")
    if updatep is not None:
        jobs.update_pycompmusic.apply_async([hostname], queue=hostname)
        return redirect('docserver-worker', hostname)
    restart = request.GET.get("restart")
    if restart is not None:
        jobs.shutdown_celery(hostname)
        return redirect('docserver-worker', hostname)

    try:
        wk = models.Worker.objects.get(hostname=hostname)
    except models.Worker.DoesNotExist:
        wk = None

    workername = "celery@%s" % hostname
    i = app.control.inspect([workername])
    tasks = i.active()
    active = []
    if tasks:
        workertasks = tasks[workername]
        for t in workertasks:
            thetask = understand_task(t)
            active.append(thetask)

    reservedtasks = i.reserved()
    reserved = []
    if reservedtasks:
        workerreserved = reservedtasks[workername]
        for t in workerreserved:
            thetask = understand_task(t)
            reserved.append(thetask)

    stats = i.clock()
    uptime = None
    if stats:
        uptime = stats.get(workername, {}).get("clock")
        delta = datetime.timedelta(seconds=uptime)
        start = datetime.datetime.now() - delta

    if not tasks and not reservedtasks:
        state = "Offline"
    elif wk and wk.state == models.Worker.UPDATING:
        state = "Updating"
    elif len(active) or len(reserved):
        state = "Active"
    elif len(active) == 0 and len(reserved) == 0:
        state = "Idle"

    ret = {"worker": wk, "state": state, "active": active,
            "reserved": reserved, "uptime": start}
    return render(request, 'docserver/worker.html', ret)


@user_passes_test(is_staff)
def update_all_workers(request):
    jobs.update_all_workers()
    return redirect('docserver-manager')

@user_passes_test(is_staff)
def addmodule(request):
    # TODO: It would be cool if we just search for all modules in the `extractors` module
    #       that haven't been installed yet
    if request.method == "POST":
        form = forms.ModuleForm(request.POST)
        if form.is_valid():
            module = form.cleaned_data["module"]
            collections = []
            for i in form.cleaned_data['collections']:
                collections.append(get_object_or_404(models.Collection, pk=int(i)))
            jobs.create_module(module, collections)
            return redirect('docserver-manager')
    else:
        form = forms.ModuleForm()
    ret = {"form": form}
    return render(request, 'docserver/addmodule.html', ret)

@user_passes_test(is_staff)
def module(request, module):
    module = get_object_or_404(models.Module, pk=module)
    versions = module.versions.all()
    confirmversion = False
    confirmmodule = False
    form = forms.ModuleEditForm(instance=module)
    if request.method == "POST":
        if request.POST.get("deleteversion"):
            version = request.POST.get("version")
            versions = versions.filter(pk=version)
            confirmversion = version
        elif request.POST.get("confirmversion"):
            version = request.POST.get("version")
            jobs.delete_moduleversion.delay(version)
        elif request.POST.get("deletemodule"):
            # The module id is already in the argument to this method
            # so we don't get it from POST like the mod-version above.
            confirmmodule = module.pk
        elif request.POST.get("confirmmodule"):
            jobs.delete_module.delay(module.pk)
        elif request.POST.get("update"):
            form = forms.ModuleEditForm(request.POST, instance=module)
            form.save()

    ret = {"module": module, "versions": versions, "form": form, "confirmversion": confirmversion, "confirmmodule": confirmmodule}
    return render(request, 'docserver/module.html', ret)

@user_passes_test(is_staff)
def collection(request, slug):
    collection = get_object_or_404(models.Collection, slug=slug)
    ret = {"collection": collection}
    return render(request, 'docserver/collection.html', ret)

@user_passes_test(is_staff)
def collectionversion(request, slug, version, type):
    collection = get_object_or_404(models.Collection, slug=slug)
    mversion = get_object_or_404(models.ModuleVersion, pk=version)

    run = request.GET.get("run")
    if run:
        document = models.Document.objects.get(external_identifier=run)
        jobs.process_document.delay(document.pk, mversion.pk)
        return redirect('docserver-collectionversion', args=[type, slug, version])

    processedfiles = []
    unprocessedfiles = []
    if type == "processed":
        processedfiles = mversion.processed_files(collection)
    elif type == "unprocessed":
        unprocessedfiles = mversion.unprocessed_files(collection)
    ret = {"collection": collection,
            "modulever": mversion,
            "type": type,
            "unprocessedfiles": unprocessedfiles,
            "processedfiles": processedfiles}
    return render(request, 'docserver/collectionversion.html', ret)

@user_passes_test(is_staff)
def file(request, slug, uuid, version=None):
    collection = get_object_or_404(models.Collection, slug=slug)
    doc = collection.documents.get_by_external_id(uuid)

    derived = doc.derivedfiles.all()
    if version:
        version = get_object_or_404(models.ModuleVersion, pk=version)
        modulederived = derived.filter(module_version=version)
    else:
        modulederived = []

    outputs = doc.nestedderived()

    ret = {"document": doc,
           "collection": collection,
           "modulever": version,
           "outputs": outputs,
           "modulederived": modulederived}
    return render(request, 'docserver/file.html', ret)

