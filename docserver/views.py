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

import json
import datetime
import inspect
import pkgutil
import imp
import os

from django.http import HttpResponse, Http404
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms.models import modelformset_factory

from docserver import models
from docserver import forms
from docserver import jobs
from docserver import serializers
from docserver import util
from docserver import log
from dunya.celery import app
import dashboard

from compmusic import extractors

from rest_framework import authentication
from rest_framework import exceptions
from rest_framework import generics
from rest_framework import parsers
from rest_framework import response
from rest_framework import status
from rest_framework import permissions

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

class StaffWritePermission(permissions.IsAuthenticated):
    """ An extension of the IsAuthenticated permission which only lets
        staff members perform POST methods """
    def has_permission(self, request, view):
        perm = super(StaffWritePermission, self).has_permission(request, view)
        if request.method == "POST":
            return perm and request.user.is_staff
        else:
            return perm

class DocumentDetailExternal(generics.CreateAPIView, generics.RetrieveAPIView):
    lookup_field = 'external_identifier'
    queryset = models.Document.objects.all()
    serializer_class = serializers.DocumentSerializer
    permission_classes = (StaffWritePermission, )

class SourceFileException(Exception):
    def __init__(self, status_code, message):
        super(SourceFileException, self).__init__(self)
        self.status_code = status_code
        self.message = message

class SourceFile(generics.CreateAPIView, generics.UpdateAPIView):
    parser_classes = (parsers.MultiPartParser,)
    permission_classes = (StaffWritePermission, )

    def _write_to_disk(self, file, filepath):
        """ write the file object `file` to disk at `filepath'"""

        size = 0
        try:
            with open(filepath, 'wb') as dest:
                for chunk in file.chunks():
                    size += len(chunk)
                    dest.write(chunk)
        except IOError as e:
            raise
        return size

    def _save_file(self, external_identifier, file_type, file):
        try:
            document = models.Document.objects.get(external_identifier=external_identifier)
        except models.Document.DoesNotExist:
            data = {'detail': 'No document with this id'}
            return response.Response(data, status=status.HTTP_404_NOT_FOUND)
        try:
            sft = models.SourceFileType.objects.get(slug=file_type)
        except models.SourceFileType.DoesNotExist:
            data = {'detail': 'No filetype with this slug'}
            return response.Response(data, status=status.HTTP_404_NOT_FOUND)

        if not file:
            data = {'detail': 'Need exactly one file called "file"'}
            return response.Response(data, status=status.HTTP_400_BAD_REQUEST)

        root = document.get_absolute_path()

        mbid = external_identifier
        mb = mbid[:2]
        slug = sft.slug
        ext = sft.extension
        filedir = os.path.join(mb, mbid, slug)
        datadir = os.path.join(root, sft.stype, filedir)

        try:
            os.makedirs(datadir)
        except OSError:
            print "Error making directory", datadir
            pass

        filename = "%s-%s.%s" % (mbid, slug, ext)
        filepath = os.path.join(models.Collection.DATA_DIR, filedir, filename)

        try:
            size = self._write_to_disk(file, filepath)
        except IOError as e:
            data = {'detail': 'Cannot write file'}
            return response.Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        sf, created = models.SourceFile.objects.get_or_create(document=document, file_type=sft, path=filepath, defaults={"size": size})
        if created:
            retstatus = status.HTTP_201_CREATED
            data = {'detail': 'created'}
        else:
            retstatus = status.HTTP_200_OK
            data = {'detail': 'updated'}
        return response.Response(data, status=retstatus)

    def create(self, request, external_identifier, file_type):
        file = request.data.get("file")
        return self._save_file(external_identifier, file_type, file)

    def update(self, request, external_identifier, file_type):
        file = request.data.get("file")
        return self._save_file(external_identifier, file_type, file)


class DocumentDetail(generics.RetrieveAPIView):
    lookup_field = 'pk'
    queryset = models.Document.objects.all()
    serializer_class = serializers.DocumentSerializer

def download_external(request, uuid, ftype):
    # Test authentication. We support a rest-framework token
    # or a logged-in user
    user = request.user
    try:
        t = auther.authenticate(request)
        if t:
            user = t[0]
    except exceptions.AuthenticationFailed:
        pass
    
    try:
        doc = models.Document.objects.get(external_identifier=uuid)
    except models.Document.DoesNotExist:
        raise NoFileException("Cannot find a document with id %s" % documentid)

    has_access = util.user_has_access(user, doc, ftype)
    if not has_access:
        return HttpResponse("Not logged in", status=401)
 
    try:
        version = request.GET.get("v")
        subtype = request.GET.get("subtype")
        part = request.GET.get("part")
        filepart = util._docserver_get_part(uuid, ftype, subtype, part, version)

        fname = filepart.fullpath
        mimetype = filepart.mimetype

        ratelimit = "off"
        if util.has_rate_limit(user, doc, ftype):
            # 200k
            ratelimit = 200 * 1024

        # TODO: We should ratelimit mp3 requests, but not any others,
        # so we need a different path for nginx for these ones
        response = sendfile(request, fname, mimetype=mimetype)
        response['X-Accel-Limit-Rate'] = ratelimit

        return response
    except util.TooManyFilesException as e:
        return HttpResponseBadRequest(e)
    except util.NoFileException as e:
        return HttpResponseNotFound(e)

#### Essentia manager

def is_staff(user):
    return user.is_staff

@user_passes_test(is_staff)
def manager(request):
    # Add a new worker to the cluster
    register = request.GET.get("register")
    if register is not None:
        jobs.register_host.apply_async([register], queue=register)
        return redirect('docserver-manager')
    if request.method == "POST":
        # Update essentia and pycompmusic on all workers
        update = request.POST.get("updateall")
        if update is not None:
            jobs.update_all_workers(request.user.username)
            return redirect('docserver-manager')
        # Process a module version
        run = request.POST.get("run")
        if run is not None:
            jobs.run_module(int(run))
            return redirect('docserver-manager')

    modules = models.Module.objects.all().order_by('name')
    collections = models.Collection.objects.all()

    inspect = app.control.inspect()
    # TODO: Load the task data via ajax, so the page loads quickly
    try:
        hosts = inspect.active()
    except:
        hosts = None
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

    ret = {"modules": modules, "collections": collections, "workers": workers,
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
    user = request.user.username

    updatee = request.GET.get("updateessentia")
    if updatee is not None:
        log.log_worker_action(hostname, user, "updateessentia")
        jobs.update_essentia.apply_async([hostname], queue=hostname)
        return redirect('docserver-worker', hostname)
    updatep = request.GET.get("updatepcm")
    if updatep is not None:
        log.log_worker_action(hostname, user, "updatepycm")
        jobs.update_pycompmusic.apply_async([hostname], queue=hostname)
        return redirect('docserver-worker', hostname)
    restart = request.GET.get("restart")
    if restart is not None:
        log.log_worker_action(hostname, user, "restart")
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

    if not tasks and not reservedtasks:
        state = "Offline"
    elif wk and wk.state == models.Worker.UPDATING:
        state = "Updating"
    elif len(active) or len(reserved):
        state = "Active"
    elif len(active) == 0 and len(reserved) == 0:
        state = "Idle"

    processed_files = log.get_processed_files(hostname)
    recent = []
    for p in processed_files:
        try:
            collection = models.Collection.objects.get(collectionid=p["collection"])
            document = collection.documents.get(external_identifier=p["recording"])
            modver = models.ModuleVersion.objects.get(pk=p["moduleversion"])
            recent.append({"document": document,
                           "collection": collection,
                           "modulever": modver,
                           "date": p["date"]})
        except ObjectDoesNotExist:
            pass

    actions = log.get_worker_actions(hostname)
    workerlog = []
    for a in actions:
        date = datetime.datetime.strptime(a["date"], "%Y-%m-%dT%H:%M:%S.%f")
        workerlog.append({"date": date, "action": a["action"]})

    ret = {"worker": wk, "state": state, "active": active,
           "reserved": reserved, "recent": recent, "workerlog": workerlog}
    return render(request, 'docserver/worker.html', ret)


@user_passes_test(is_staff)
def update_all_workers(request):
    jobs.update_all_workers()
    return redirect('docserver-manager')

def get_module_source(modulename):
    """ Given a module dotted path (string), see how it can be
    imported (.py or .pyc)
    returns imp.PY_SOURCE, imp.PY_COMPILED, or imp.C_EXTENSION"""
    pkgname, modname = modulename.rsplit(".", 1)
    # easiest way to get the path of the module
    package = __import__(pkgname, fromlist="dummy")
    print "package path", package.__path__
    moddata = imp.find_module(modname, package.__path__)
    desc = moddata[2]
    return desc[2]

def extractor_modules():
    ret = []
    modules = models.Module.objects
    for importer, modname, ispkg in pkgutil.walk_packages(extractors.__path__, "compmusic.extractors."):
        if not ispkg:
            stype = get_module_source(modname)
            if stype == imp.PY_SOURCE:
                module = __import__(modname, fromlist="dummy")
                for name, ftype in inspect.getmembers(module, inspect.isclass):
                    if issubclass(ftype, extractors.ExtractorModule):
                        classname = "%s.%s" % (modname, name)
                        if not modules.filter(module=classname).exists():
                            ret.append(classname)
    return ret

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
            return redirect('docserver-manager')
    else:
        form = forms.ModuleForm()
    newmodules = extractor_modules()
    ret = {"form": form, "newmodules": newmodules}
    return render(request, 'docserver/addmodule.html', ret)

@user_passes_test(is_staff)
def module(request, module):
    module = get_object_or_404(models.Module, pk=module)
    versions = module.versions.all()
    confirmversion = False
    confirmmodule = False
    form = forms.ModuleEditForm(instance=module)
    if request.method == "POST":
        # Delete a module version
        if request.POST.get("deleteversion"):
            version = request.POST.get("version")
            versions = versions.filter(pk=version)
            confirmversion = version
        # Confirm deleting a module version
        elif request.POST.get("confirmversion"):
            version = request.POST.get("version")
            jobs.delete_moduleversion.delay(version)
        # Delete an entire module
        elif request.POST.get("deletemodule"):
            # The module id is already in the argument to this method
            # so we don't get it from POST like the mod-version above.
            confirmmodule = module.pk
        # Confirm deleting entire module
        elif request.POST.get("confirmmodule"):
            jobs.delete_module.delay(module.pk)
        # Update list of collections for this module
        elif request.POST.get("update"):
            form = forms.ModuleEditForm(request.POST, instance=module)
            form.save()
        # Scan for a new version
        elif request.POST.get("newversion"):
            jobs.get_latest_module_version(module.pk)
            return redirect('docserver-module', module.pk)
        # Process a module (specific version)
        run = request.POST.get("runversion")
        if run is not None:
            jobs.run_module(module.pk, int(run))
            return redirect('docserver-module', module.pk)

    ret = {"module": module, "versions": versions, "form": form, "confirmversion": confirmversion, "confirmmodule": confirmmodule}
    return render(request, 'docserver/module.html', ret)

@user_passes_test(is_staff)
def delete_collection(request, slug):
    c = get_object_or_404(models.Collection, slug=slug)

    if request.method == "POST":
        delete = request.POST.get("delete")
        if delete.lower().startswith("yes"):
            msg = "The collection %s and all its documents are being deleted" % c.name
            messages.add_message(request, messages.INFO, msg)
            jobs.delete_collection.delay(c.pk)
            return redirect("docserver-manager")
        elif delete.lower().startswith("no"):
            return redirect("docserver-collection", c.slug)

    modules = models.Module.objects.filter(versions__derivedfile__document_collections=c).distinct()

    ret = {"collection": c, "modules": modules}
    return render(request, 'docserver/delete_collection.html', ret)

@user_passes_test(is_staff)
def addcollection(request):
    PermissionFormSet = modelformset_factory(models.CollectionPermission, fields=("permission", "source_type", "streamable"), extra=2)
    if request.method == 'POST':
        form = forms.CollectionForm(request.POST)
        permission_form = PermissionFormSet(request.POST)
        if form.is_valid() and permission_form.is_valid():
            col = form.save()
            coll_perms = permission_form.save(commit=False)
            for coll_perm in coll_perms:
                coll_perm.collection = col
                coll_perm.save()
            return redirect('docserver-manager')
    else:
        form = forms.CollectionForm()
        permission_form = PermissionFormSet()
    ret = {"form": form, "permission_form": permission_form, "mode": "add"}
    return render(request, 'docserver/addcollection.html', ret)

@user_passes_test(is_staff)
def editcollection(request, slug):
    coll = get_object_or_404(models.Collection, slug=slug)
    file_types = models.SourceFileType.objects.filter(sourcefile__document__collections=coll).distinct()
    PermissionFormSet = modelformset_factory(models.CollectionPermission, fields=("permission", "source_type", "streamable"), extra=2)
    if request.method == 'POST':
        form = forms.EditCollectionForm(request.POST, instance=coll)
        permission_form = PermissionFormSet(request.POST)
        if form.is_valid() and permission_form.is_valid():
            coll = form.save()
            coll_perms = permission_form.save(commit=False)
            for coll_perm in coll_perms:
                coll_perm.collection = coll
                coll_perm.save()
            return redirect(coll.get_absolute_url())
    else:
        form = forms.EditCollectionForm(instance=coll)
        permission_form = PermissionFormSet(queryset=models.CollectionPermission.objects.filter(collection=coll))
    ret = {"form": form, "permission_form": permission_form, "mode": "edit", "file_types": file_types}
    return render(request, 'docserver/addcollection.html', ret)

@user_passes_test(is_staff)
def collection(request, slug):
    collection = get_object_or_404(models.Collection, slug=slug)

    if request.method == "POST":
        delete = request.POST.get("delete")
        if delete is not None:
            jobs.delete_collection.delay(collection.pk)
        run = request.POST.get("run")
        if run is not None:
            jobs.run_module_on_collection.delay(collection.pk, int(run))

    ret = {"collection": collection}
    return render(request, 'docserver/collection.html', ret)

@user_passes_test(is_staff)
def collectionfiles(request, slug):
    collection = get_object_or_404(models.Collection, slug=slug)

    documents = collection.documents.all()
    paginator = Paginator(documents, 50)

    page = request.GET.get('page')
    try:
        documents = paginator.page(page)
    except PageNotAnInteger:
        documents = paginator.page(1)
    except EmptyPage:
        documents = paginator.page(paginator.num_pages)

    ret = {"collection": collection, "documents": documents}
    return render(request, 'docserver/collectionfiles.html', ret)

@user_passes_test(is_staff)
def collectionversion(request, slug, version, type):
    collection = get_object_or_404(models.Collection, slug=slug)
    mversion = get_object_or_404(models.ModuleVersion, pk=version)

    run = request.GET.get("run")
    if run:
        document = models.Document.objects.get(external_identifier=run)
        jobs.process_document.delay(document.pk, mversion.pk)
        return redirect('docserver-collectionversion', type, slug, version)

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

    doc = models.Document.objects.get(external_identifier=uuid, collections=collection)

    derived = doc.derivedfiles.all()
    showderived = False
    if version:
        version = get_object_or_404(models.ModuleVersion, pk=version)
        modulederived = derived.filter(module_version=version)
        showderived = True
    else:
        modulederived = []

    outputs = doc.nestedderived()

    ret = {"document": doc,
           "collection": collection,
           "modulever": version,
           "outputs": outputs,
           "modulederived": modulederived,
           "showderived": showderived}
    return render(request, 'docserver/file.html', ret)

@user_passes_test(is_staff)
def addfiletype(request):
    if request.method == 'POST':
        form = forms.SourceFileTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('docserver-filetypes')
    else:
        form = forms.SourceFileTypeForm()
    ret = {"form": form, "mode": "add"}
    return render(request, 'docserver/addfiletype.html', ret)

@user_passes_test(is_staff)
def filetypes(request):
    filetypes = models.SourceFileType.objects.all()
    ret = {"filetypes": filetypes}
    return render(request, 'docserver/filetypes.html', ret)

@user_passes_test(is_staff)
def filetype(request, slug):
    ft = get_object_or_404(models.SourceFileType, slug=slug)
    ret = {"filetype": ft}
    return render(request, 'docserver/filetype.html', ret)

@user_passes_test(is_staff)
def editfiletype(request, slug):
    ft = get_object_or_404(models.SourceFileType, slug=slug)
    if request.method == 'POST':
        form = forms.SourceFileTypeForm(request.POST, instance=ft)
        if form.is_valid():
            form.save()
            return redirect('docserver-filetypes')
    else:
        form = forms.SourceFileTypeForm(instance=ft)
    ret = {"form": form, "mode": "edit"}
    return render(request, 'docserver/addfiletype.html', ret)
