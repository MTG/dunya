from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse

from dashboard import models
from dashboard import forms
import compmusic
import os
import importlib
import json

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

def collection(request, uuid):
    c = models.Collection.objects.get(pk=uuid)
    log = models.CollectionLogMessage.objects.filter(collection=c)
    releases = models.MusicbrainzRelease.objects.filter(collection=c)
    folders = models.CollectionDirectory.objects.filter(collection=c, musicbrainzrelease__isnull=True)
    ret = {"collection": c, "log_messages": log, "releases": releases, "folders": folders}
    return render(request, 'dashboard/collection.html', ret)

def release(request, uuid):
    release = models.MusicbrainzRelease.objects.get(pk=uuid)
    files = release.collectiondirectory_set.order_by('path').all()

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

    ret = {"release": release, "files": files, "pendingtest": pendingtest, "finishedtest": finishedtest}
    return render(request, 'dashboard/release.html', ret)

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

def directory(request, dirid):
    """ A directory that wasn't matched to a release in the collection.
    This could be because it has no release tags, or the release isn't in
    the collection.
    We want to group together as much common information as possible, and
    link to musicbrainz if we can.
    """

    directory = models.CollectionDirectory.objects.get(pk=dirid)
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

    got_release = len(releaseids) == 1
    # This won't work if there are more than 1 lead artist?
    got_artist = len(artistids) == 1
    print "releaseids", releaseids
    print "artistids", artistids

    ret = {"files": sorted(files), "directory": directory, "got_release": got_release, "got_artist": got_artist}
    if got_release:
        ret["releasename"] = list(releasename)[0]
        ret["releaseid"] = list(releaseids)[0]
    if got_artist:
        ret["artistname"] = list(artistname)[0]
        ret["artistid"] = list(artistids)[0]
    return render(request, 'dashboard/directory.html', ret)
