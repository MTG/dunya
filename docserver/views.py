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
import ast
import datetime
import importlib.machinery
import importlib.util
import inspect
import json
import os
import pkgutil

from dashboard import extractors
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms.models import modelformset_factory
from django.http import HttpResponse, Http404
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import authentication
from rest_framework import exceptions
from rest_framework import generics
from rest_framework import parsers
from rest_framework import permissions
from rest_framework import response
from rest_framework import status
from rest_framework.exceptions import ValidationError, MethodNotAllowed
from rest_framework.serializers import BaseSerializer
from django_sendfile import sendfile

import dashboard.models
import docserver
from docserver import forms
from docserver import jobs
from docserver import log
from docserver import models
from docserver import serializers
from docserver import util
from dunya.celery import app

auther = authentication.TokenAuthentication()


def index(request):
    return HttpResponse("Hello docserver")


class CollectionList(generics.ListAPIView):
    queryset = models.Collection.objects.all()
    serializer_class = serializers.CollectionListSerializer


class CollectionDetail(generics.RetrieveAPIView):
    lookup_field = "slug"
    queryset = models.Collection.objects.all()
    serializer_class = serializers.CollectionDetailSerializer


class StaffWritePermission(permissions.IsAuthenticated):
    """An extension of the IsAuthenticated permission which only lets
    staff members perform POST methods"""

    def has_permission(self, request, view):
        perm = super().has_permission(request, view)
        if request.method == "POST":
            return perm and request.user.is_staff
        else:
            return perm


class DocumentDetail(generics.CreateAPIView, generics.RetrieveAPIView):
    lookup_field = "external_identifier"
    serializer_class = serializers.DocumentSerializer
    permission_classes = (StaffWritePermission,)

    def get_queryset(self):
        if "slug" in self.kwargs:
            slug = self.kwargs["slug"]
            collection = get_object_or_404(models.Collection.objects, slug=slug)
            return collection.documents
        return models.Document.objects

    def create(self, request, external_identifier):
        title = request.data.get("title", None)
        slug = request.data.get("collection", None)

        if not slug:
            raise ValidationError("Slug not present in request")

        try:
            collection = models.Collection.objects.get(slug=slug)
        except models.Collection.DoesNotExist:
            raise Http404("Invalid collection slug")
        doc = util.docserver_create_document(collection.collectionid, external_identifier, title)
        serialized = serializers.DocumentSerializer(doc)
        return response.Response(serialized.data, status=status.HTTP_201_CREATED)


class SourceFileException(Exception):
    def __init__(self, status_code, message):
        super().__init__(self)
        self.status_code = status_code
        self.message = message


class SourceFile(generics.CreateAPIView, generics.UpdateAPIView, generics.RetrieveAPIView):
    parser_classes = (parsers.MultiPartParser,)
    permission_classes = (StaffWritePermission,)
    serializer_class = serializers.SourceFileSerializer

    def get_queryset(self):
        identifier = self.kwargs.get("external_identifier")
        if identifier:
            return models.SourceFile.objects.filter(external_identifier=identifier)
        return models.SourceFile.objects

    def _save_file(self, external_identifier, file_type, file):
        try:
            document = models.Document.objects.get(external_identifier=external_identifier)
        except models.Document.DoesNotExist:
            data = {"detail": "No document with this id"}
            return response.Response(data, status=status.HTTP_404_NOT_FOUND)
        try:
            sft = models.SourceFileType.objects.get(slug=file_type)
        except models.SourceFileType.DoesNotExist:
            data = {"detail": "No filetype with this slug"}
            return response.Response(data, status=status.HTTP_404_NOT_FOUND)

        if not file:
            data = {"detail": 'Need exactly one file called "file"'}
            return response.Response(data, status=status.HTTP_400_BAD_REQUEST)

        try:
            sf, created = util.docserver_upload_and_save_file(document.id, sft.id, file)
        except OSError as e:
            data = {"detail": "Cannot write file"}
            return response.Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if created:
            retstatus = status.HTTP_201_CREATED
            data = {"detail": "created"}
        else:
            retstatus = status.HTTP_200_OK
            data = {"detail": "updated"}
        return response.Response(data, status=retstatus)

    def get(self, request, external_identifier, file_type):
        raise MethodNotAllowed("GET")

    def create(self, request, external_identifier, file_type):
        file = request.data.get("file")
        return self._save_file(external_identifier, file_type, file)

    def update(self, request, external_identifier, file_type):
        file = request.data.get("file")
        return self._save_file(external_identifier, file_type, file)


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
        return HttpResponseNotFound(f"Cannot find a document with id {uuid}")

    # if ftype is a sourcetype and it has streamable set, and
    # referrer is dunya, then has_access is true (but we rate-limit)
    referrer = request.META.get("HTTP_REFERER")
    good_referrer = False
    if referrer:
        if "dunya.compmusic.upf.edu" in referrer or "dunya.upf.edu" in referrer:
            good_referrer = True

    has_access = util.user_has_access(user, doc, ftype, good_referrer)
    if not has_access:
        return HttpResponse("Not logged in", status=401)

    try:
        version = request.GET.get("v")
        subtype = request.GET.get("subtype")
        part = request.GET.get("part")

        # This could be a SourceFile, or DerivedFile
        result = doc.get_file(ftype, subtype, part, version)
        if isinstance(result, models.SourceFile):
            fname = result.fullpath
        else:
            if part is None:
                part = 1
            fname = result.full_path_for_part(part)

        mimetype = result.mimetype
        ratelimit = "off"
        if util.has_rate_limit(user, doc, ftype):
            # 200k
            ratelimit = 200 * 1024

        # TODO: We should ratelimit mp3 requests, but not any others,
        # so we need a different path for nginx for these ones
        response = sendfile(request, fname, mimetype=mimetype)
        response["X-Accel-Limit-Rate"] = ratelimit

        return response
    except docserver.exceptions.TooManyFilesException as e:
        return HttpResponseBadRequest(e)
    except docserver.exceptions.NoFileException as e:
        return HttpResponseNotFound(e)


# Essentia manager
def is_staff(user):
    return user.is_staff


@user_passes_test(is_staff)
def manager(request):
    # Add a new worker to the cluster
    register = request.GET.get("register")
    if register is not None:
        # All hosts should listen on a queue named themselves, so that
        # when we register it, we get the data from the correct host
        jobs.register_host.apply_async([register], queue=register)
        return redirect("docserver-manager")
    if request.method == "POST":
        # Process a module version
        run = request.POST.get("run")
        if run is not None:
            jobs.run_module(int(run))
            return redirect("docserver-manager")

    collections = models.Collection.objects.all()
    modules = models.Module.objects.order_by("name").all()

    ret = {"collections": collections, "modules": modules}
    return render(request, "docserver/manager.html", ret)


@user_passes_test(is_staff)
def modules_status(request):
    modules = []
    for m in models.Module.objects.all().order_by("name"):
        modules.append(
            {
                "disabled": m.disabled,
                "abs_url": m.get_absolute_url(),
                "name": m.name,
                "module": m.module,
                "latest_version_number": m.latest_version_number(),
                "processed_files": len(m.processed_files()),
                "unprocessed_files": len(m.unprocessed_files()),
                "pk": m.pk,
                "collections": [c.name for c in m.collections.all()],
            }
        )
    ret = {"modules": modules}
    return HttpResponse(json.dumps(ret), content_type="application/json")


@user_passes_test(is_staff)
def workers_status(request):
    inspect = app.control.inspect()
    latestpycm = models.PyCompmusicVersion.objects.order_by("-commit_date").first()
    latestessentia = models.EssentiaVersion.objects.order_by("-commit_date").first()

    try:
        hosts = inspect.active()
    except:
        hosts = None
    workerobs = models.Worker.objects.all()
    workerkeys = [f"celery@{w.hostname}" for w in workerobs]
    if hosts:
        hostkeys = hosts.keys()
        workers = list(set(workerkeys) & set(hostkeys))
        neww = []
        for w in workers:
            host = w.split("@")[1]
            theworker = workerobs.get(hostname=host)
            essentia = theworker.essentia
            pyc = theworker.pycompmusic
            num_proc = len(hosts[w])
            if theworker.state == models.Worker.UPDATING:
                state = "Updating"
            elif num_proc:
                state = "Active"
            else:
                state = "Idle"
            if essentia:
                e = {"version": essentia.sha1, "link": essentia.short_link()}
            else:
                e = {}
            if pyc:
                p = {"version": pyc.sha1, "link": pyc.short_link()}
            else:
                p = {}
            neww.append({"host": host, "number": num_proc, "state": state, "worker": {"essentia": e, "pyc": p}})

        workers = neww
        newworkers = list(set(hostkeys) - set(workerkeys))
        newworkers = [w.split("@")[1] for w in newworkers]
        inactiveworkers = list(set(workerkeys) - set(hostkeys))
        inactiveworkers = [w.split("@")[1] for w in inactiveworkers]
    else:
        workers = []
        newworkers = []
        inactiveworkers = [w.split("@")[1] for w in workerkeys]
    ret = {
        "workers": workers,
        "newworkers": newworkers,
        "inactiveworkers": inactiveworkers,
        "latestpycm": latestpycm.sha1,
        "latestessentia": latestessentia.sha1,
    }

    return HttpResponse(json.dumps(ret), content_type="application/json")


def understand_task(task):
    tname = task["name"]
    try:
        args = ast.literal_eval(task["args"])
    except SyntaxError:
        args = []
    thetask = {"name": tname}
    # Magic task splitter
    if tname == "dashboard.jobs.load_musicbrainz_collection":
        thetask["type"] = "loadcollection"
        thetask["nicename"] = "Import musicbrainz collection"
        collectionid = args[0]
        coll = dashboard.models.Collection.objects.get(collectionid=collectionid)
        thetask["collection"] = coll
    elif tname == "dashboard.jobs.import_all_releases" or tname == "dashboard.jobs.force_import_all_releases":
        thetask["type"] = "importreleases"
        thetask["nicename"] = "Import releases in collection"
        collectionid = args[0]
        coll = dashboard.models.Collection.objects.get(collectionid=collectionid)
        thetask["collection"] = coll
    elif tname == "dashboard.jobs.import_single_release":
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
    try:
        wk = models.Worker.objects.get(hostname=hostname)
    except models.Worker.DoesNotExist:
        wk = None

    workername = f"celery@{hostname}"
    i = app.control.inspect([workername])
    try:
        tasks = i.active()
    except ConnectionResetError:
        tasks = []
    active = []
    if tasks:
        workertasks = tasks[workername]
        for t in workertasks:
            thetask = understand_task(t)
            active.append(thetask)

    try:
        reservedtasks = i.reserved()
    except ConnectionResetError:
        reservedtasks = []
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
            collection = models.Collection.objects.get(collectionid=p.get("collection"))
            document = collection.documents.get(external_identifier=p.get("recording"))
            modver = models.ModuleVersion.objects.get(pk=p.get("moduleversion"))
            recent.append({"document": document, "collection": collection, "modulever": modver, "date": p.get("date")})
        except ObjectDoesNotExist:
            pass

    actions = log.get_worker_actions(hostname)
    workerlog = []
    for a in actions:
        date = datetime.datetime.strptime(a["date"], "%Y-%m-%dT%H:%M:%S.%f")
        workerlog.append({"date": date, "action": a["action"]})

    ret = {
        "worker": wk,
        "state": state,
        "active": active,
        "reserved": reserved,
        "recent": recent,
        "workerlog": workerlog,
    }
    return render(request, "docserver/worker.html", ret)


def extractor_modules():
    ret = []
    errors = []
    modules = models.Module.objects
    for importer, modname, ispkg in pkgutil.walk_packages(extractors.__path__, "dashboard.extractors."):
        if not ispkg:
            spec = importlib.util.find_spec(modname)
            path, ext = os.path.splitext(spec.origin)
            if ext in importlib.machinery.SOURCE_SUFFIXES:
                try:
                    module = __import__(modname, fromlist="dummy")
                    for name, ftype in inspect.getmembers(module, inspect.isclass):
                        if issubclass(ftype, extractors.ExtractorModule):
                            classname = f"{modname}.{name}"
                            if not modules.filter(module=classname).exists():
                                ret.append(classname)
                except ImportError:
                    errors.append(modname)
    return ret, errors


@user_passes_test(is_staff)
def addmodule(request):
    if request.method == "POST":
        form = forms.ModuleForm(request.POST)
        if form.is_valid():
            module = form.cleaned_data["module"]
            collections = []
            for i in form.cleaned_data["collections"]:
                collections.append(get_object_or_404(models.Collection, pk=int(i)))
            jobs.create_module(module, collections)
            return redirect("docserver-manager")
    else:
        form = forms.ModuleForm()
    newmodules, errors = extractor_modules()
    ret = {"form": form, "newmodules": newmodules, "errormodules": errors}
    return render(request, "docserver/addmodule.html", ret)


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
            return redirect("docserver-module", module.pk)
        # Process a module (specific version)
        run = request.POST.get("runversion")
        if run is not None:
            jobs.run_module(module.pk, int(run))
            return redirect("docserver-module", module.pk)

    logmessages = models.DocumentLogMessage.objects.filter(moduleversion__module=module)[:20]

    ret = {
        "module": module,
        "versions": versions,
        "form": form,
        "confirmversion": confirmversion,
        "confirmmodule": confirmmodule,
        "logs": logmessages,
    }
    return render(request, "docserver/module.html", ret)


@user_passes_test(is_staff)
def delete_collection(request, slug):
    c = get_object_or_404(models.Collection, slug=slug)

    if request.method == "POST":
        delete = request.POST.get("delete")
        if delete.lower().startswith("yes"):
            msg = f"The collection {c.name} and all its documents are being deleted"
            messages.add_message(request, messages.INFO, msg)
            jobs.delete_collection.delay(c.pk)
            return redirect("docserver-manager")
        elif delete.lower().startswith("no"):
            return redirect("docserver-collection", c.slug)

    modules = models.Module.objects.filter(versions__derivedfile__document_collections=c).distinct()

    ret = {"collection": c, "modules": modules}
    return render(request, "docserver/delete_collection.html", ret)


@user_passes_test(is_staff)
def addcollection(request):
    PermissionFormSet = modelformset_factory(
        models.CollectionPermission, fields=("permission", "source_type", "streamable"), extra=2
    )
    if request.method == "POST":
        form = forms.CollectionForm(request.POST)
        permission_form = PermissionFormSet(request.POST)
        if form.is_valid() and permission_form.is_valid():
            col = form.save()
            coll_perms = permission_form.save(commit=False)
            for coll_perm in coll_perms:
                coll_perm.collection = col
                coll_perm.save()
            return redirect("docserver-manager")
    else:
        form = forms.CollectionForm()
        permission_form = PermissionFormSet()
    ret = {"form": form, "permission_form": permission_form, "mode": "add"}
    return render(request, "docserver/addcollection.html", ret)


@user_passes_test(is_staff)
def editcollection(request, slug):
    coll = get_object_or_404(models.Collection, slug=slug)
    file_types = models.SourceFileType.objects.filter(sourcefile__document__collections=coll).distinct()
    PermissionFormSet = modelformset_factory(
        models.CollectionPermission, fields=("permission", "source_type", "streamable"), extra=2
    )
    if request.method == "POST":
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
    return render(request, "docserver/addcollection.html", ret)


@user_passes_test(is_staff)
def delete_derived_files(request, slug, moduleversion):
    c = get_object_or_404(models.Collection, slug=slug)
    m = get_object_or_404(models.ModuleVersion, pk=moduleversion)

    if request.method == "POST":
        delete = request.POST.get("delete")
        if delete.lower().startswith("yes"):
            models.DerivedFile.objects.filter(document__collections=c, module_version=m).delete()
            return redirect("docserver-collection", c.slug)
        elif delete.lower().startswith("no"):
            return redirect("docserver-collection", c.slug)

    ret = {"collection": c, "moduleversion": m}
    return render(request, "docserver/delete_derived_files.html", ret)


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
    return render(request, "docserver/collection.html", ret)


@user_passes_test(is_staff)
def collectionfiles(request, slug):
    collection = get_object_or_404(models.Collection, slug=slug)

    documents = collection.documents.all()
    paginator = Paginator(documents, 50)

    page = request.GET.get("page")
    try:
        documents = paginator.page(page)
    except PageNotAnInteger:
        documents = paginator.page(1)
    except EmptyPage:
        documents = paginator.page(paginator.num_pages)

    ret = {"collection": collection, "documents": documents}
    return render(request, "docserver/collectionfiles.html", ret)


@user_passes_test(is_staff)
def collectionversion(request, slug, version, type):
    collection = get_object_or_404(models.Collection, slug=slug)
    mversion = get_object_or_404(models.ModuleVersion, pk=version)
    page = request.GET.get("page")

    run = request.GET.get("run")
    if run:
        document = models.Document.objects.get(external_identifier=run)
        jobs.process_document.delay(document.pk, mversion.pk)
        return redirect("docserver-collectionversion", type, slug, version)

    processedfiles = []
    unprocessedfiles = []
    if type == "processed":
        processedfiles = mversion.processed_files(collection)
        paginator = Paginator(processedfiles, 25)
        try:
            processedfiles = paginator.page(page)
        except PageNotAnInteger:
            processedfiles = paginator.page(1)
        except EmptyPage:
            processedfiles = paginator.page(paginator.num_pages)
    elif type == "unprocessed":
        unprocessedfiles = mversion.unprocessed_files(collection)
        paginator = Paginator(unprocessedfiles, 25)
        try:
            unprocessedfiles = paginator.page(page)
        except PageNotAnInteger:
            unprocessedfiles = paginator.page(1)
        except EmptyPage:
            unprocessedfiles = paginator.page(paginator.num_pages)
    ret = {
        "collection": collection,
        "modulever": mversion,
        "type": type,
        "unprocessedfiles": unprocessedfiles,
        "processedfiles": processedfiles,
    }
    return render(request, "docserver/collectionversion.html", ret)


@user_passes_test(is_staff)
def file(request, slug, uuid, version=None):
    collection = get_object_or_404(models.Collection, slug=slug)

    doc = get_object_or_404(models.Document, external_identifier=uuid, collections=collection)

    runmodule = request.GET.get("runmodule")
    if runmodule:
        mversion = models.ModuleVersion.objects.get(pk=runmodule)
        jobs.process_document.delay(doc.pk, mversion.pk)
        return redirect("docserver-file", slug, uuid, version)

    derived = doc.derivedfiles.all()
    showderived = False
    if version:
        version = get_object_or_404(models.ModuleVersion, pk=version)
        modulederived = derived.filter(module_version=version)
        showderived = True
    else:
        modulederived = []

    outputs = doc.nestedderived()

    ret = {
        "document": doc,
        "collection": collection,
        "modulever": version,
        "outputs": outputs,
        "modulederived": modulederived,
        "showderived": showderived,
    }
    return render(request, "docserver/file.html", ret)


@user_passes_test(is_staff)
def addfiletype(request):
    if request.method == "POST":
        form = forms.SourceFileTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("docserver-filetypes")
    else:
        form = forms.SourceFileTypeForm()
    ret = {"form": form, "mode": "add"}
    return render(request, "docserver/addfiletype.html", ret)


@user_passes_test(is_staff)
def filetypes(request):
    filetypes = models.SourceFileType.objects.all()
    ret = {"filetypes": filetypes}
    return render(request, "docserver/filetypes.html", ret)


@user_passes_test(is_staff)
def filetype(request, slug):
    ft = get_object_or_404(models.SourceFileType, slug=slug)
    ret = {"filetype": ft}
    return render(request, "docserver/filetype.html", ret)


@user_passes_test(is_staff)
def editfiletype(request, slug):
    ft = get_object_or_404(models.SourceFileType, slug=slug)
    if request.method == "POST":
        form = forms.SourceFileTypeForm(request.POST, instance=ft)
        if form.is_valid():
            form.save()
            return redirect("docserver-filetypes")
    else:
        form = forms.SourceFileTypeForm(instance=ft)
    ret = {"form": form, "mode": "edit"}
    return render(request, "docserver/addfiletype.html", ret)
