from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from dashboard import models
from dashboard import forms
from dashboard import jobs
import compmusic
import os
import importlib
import json

import carnatic

@login_required
def index(request):
    if request.method == 'POST':
        form = forms.AddCollectionForm(request.POST)
        if form.is_valid():
            # Import collection id
            coll_id = form.cleaned_data['collectionid']
            path = form.cleaned_data['path']
            coll_name = form.cleaned_data['collectionname']
            new_collection = models.Collection.objects.create(id=coll_id, name=coll_name, root_directory=path)
            return HttpResponseRedirect(reverse('dashboard-home'))
            # TODO: Start job to automatically import files
            # TODO: create 'not started' status rows for every file and release
    else:
        form = forms.AddCollectionForm()

    collections = models.Collection.objects.all()
    ret = {'form': form, 'collections': collections}
    return render(request, 'dashboard/index.html', ret)

@login_required
def collection(request, uuid):
    c = get_object_or_404(models.Collection, pk=uuid)

    rescandir = request.GET.get("rescandir")
    rescanmb = request.GET.get("rescanmb")
    if rescandir is not None:
        # TODO: celery
        jobs.scan_and_link(c.id)
    if rescanmb is not None:
        # TODO: Should we scan and link after this?
        jobs.update_collection(c.id)

    log = models.CollectionLogMessage.objects.filter(collection=c)
    releases = models.MusicbrainzRelease.objects.filter(collection=c)
    folders = models.CollectionDirectory.objects.filter(collection=c, musicbrainzrelease__isnull=True)
    ret = {"collection": c, "log_messages": log, "releases": releases, "folders": folders}
    return render(request, 'dashboard/collection.html', ret)

@login_required
def release(request, releaseid):
    release = get_object_or_404(models.MusicbrainzRelease, pk=releaseid)

    reimport = request.GET.get("reimport")
    if reimport is not None:
        #TODO: celery
        jobs.import_release(release.id)

    files = release.collectiondirectory_set.order_by('path').all()
    log = release.musicbrainzreleaselogmessage_set.all()

    pendingtest = release.releasestatus_set.filter(status__in=('n', 's')).all()

    finished = release.releasestatus_set.filter(status__in=('g', 'b')).all()
    finishedtest = []
    for f in finished:
        clsname = f.checker.module
        mod, dot, cls = clsname.rpartition(".")
        i = importlib.import_module(mod)
        instance = getattr(i, cls)()
        if hasattr(instance, "templatestub"):
            template = instance.templatestub
        else:
            template = None

        finishedtest.append({"checker": f,
                            "data": instance.prepare_view(json.loads(f.data)),
                            "template": template})

    ret = {"release": release, "files": files, "pendingtest": pendingtest, "finishedtest": finishedtest, "log_messages": log}
    return render(request, 'dashboard/release.html', ret)

@login_required
def file(request, fileid):
    thefile = get_object_or_404(models.CollectionFile, pk=fileid)
    pendingtest = thefile.filestatus_set.filter(status__in=('n', 's')).all()

    finished = thefile.filestatus_set.filter(status__in=('g', 'b')).all()
    finishedtest = []
    for f in finished:
        clsname = f.checker.module
        mod, dot, cls = clsname.rpartition(".")
        i = importlib.import_module(mod)
        instance = getattr(i, cls)()
        if hasattr(instance, "templatestub"):
            template = instance.templatestub
        else:
            template = None

        finishedtest.append({"checker": f,
                            "data": instance.prepare_view(json.loads(f.data)),
                            "template": template})
    ret = {"file": thefile, "pendingtest": pendingtest, "finishedtest": finishedtest}
    return render(request, 'dashboard/file.html', ret)

@login_required
def directory(request, dirid):
    """ A directory that wasn't matched to a release in the collection.
    This could be because it has no release tags, or the release isn't in
    the collection.
    We want to group together as much common information as possible, and
    link to musicbrainz if we can.
    """
    directory = get_object_or_404(models.CollectionDirectory, pk=dirid)

    rematch = request.GET.get("rematch")
    if rematch is not None:
        # TODO: Change to celery
        jobs.rematch_unknown_directory(dirid)
        directory = get_object_or_404(models.CollectionDirectory, pk=dirid)

    collection = directory.collection
    full_path = os.path.join(collection.root_directory, directory.path)
    files = os.listdir(full_path)
    meta = {}
    releaseids = set()
    releasename = set()
    artistids = set()
    artistname = set()
    for f in files:
        data = compmusic.file_metadata(os.path.join(full_path, f))
        relid = data["meta"]["releaseid"]
        relname = data["meta"]["release"]
        aname = data["meta"]["artist"]
        aid = data["meta"]["artistid"]
        if relid and relname:
            releaseids.add(relid)
            releasename.add(relname)
        if aname and aid:
            artistids.add(aid)
            artistname.add(aname)

    got_release_id = len(releaseids) == 1
    # TODO: This won't work if there are more than 1 lead artist?
    got_artist = len(artistids) == 1
    print "releaseids", releaseids
    print "artistids", artistids

    if directory.musicbrainzrelease:
        matched_release = directory.musicbrainzrelease
    else:
        matched_release = None

    ret = {"files": sorted(files), "directory": directory, "got_release_id": got_release_id, "got_artist": got_artist, "matched_release": matched_release}
    if got_release_id:
        ret["releasename"] = list(releasename)[0]
        ret["releaseid"] = list(releaseids)[0]
    if got_artist:
        ret["artistname"] = list(artistname)[0]
        ret["artistid"] = list(artistids)[0]
    return render(request, 'dashboard/directory.html', ret)

@login_required
def raagas(request):
    raagas = carnatic.models.Raaga.objects.all()
    ret = {"raagas": raagas}
    return render(request, 'dashboard/raagas.html', ret)

@login_required
def taalas(request):
    taalas = carnatic.models.Taala.objects.all()
    ret = {"taalas": taalas}
    return render(request, 'dashboard/taalas.html', ret)

@login_required
def instruments(request):
    instruments = carnatic.models.Instrument.objects.all()
    ret = {"instruments": instruments}
    return render(request, 'dashboard/instruments.html', ret)
