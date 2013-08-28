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
            jobs.load_musicbrainz_collection.delay(new_collection.id)
            return HttpResponseRedirect(reverse('dashboard-home'))
    else:
        form = forms.AddCollectionForm()

    collections = models.Collection.objects.all()
    ret = {'form': form, 'collections': collections}
    return render(request, 'dashboard/index.html', ret)

@login_required
def collection(request, uuid):
    c = get_object_or_404(models.Collection, pk=uuid)

    rescan = request.GET.get("rescan")
    if rescan is not None:
        jobs.load_musicbrainz_collection.delay(c.id)

    log = models.CollectionLogMessage.objects.filter(collection=c).order_by('-datetime')
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
    log = release.musicbrainzreleaselogmessage_set.order_by('-datetime').all()

    results = release.musicbrainzreleaseresult_set.all()
    finishedtest = []
    for f in results:
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
    print "finishedtest", finishedtest

    ret = {"release": release, "files": files, "finishedtest": finishedtest, "log_messages": log}
    return render(request, 'dashboard/release.html', ret)

@login_required
def file(request, fileid):
    thefile = get_object_or_404(models.CollectionFile, pk=fileid)
    pendingtest = thefile.collectionfileresult_set.filter(result__in=('n', 's')).all()

    finished = thefile.collectionfileresult_set.filter(result__in=('g', 'b')).all()
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
    # TODO: Raaga/taala/instrument is all duplicated code!
    raagas = carnatic.models.Raaga.objects.all()
    ret = {"items": raagas,
           "entityn": "Raaga",
           "entitynpl": "Raagas",
           "entityurl": "dashboard-raagas",
           }
    if request.method == 'POST':
        # Add aliases
        for r in raagas:
            isadd = request.POST.get("item-%s-alias" % r.id)
            if isadd is not None:
                carnatic.models.RaagaAlias.objects.create(raaga=r, name=isadd)
        # Delete alias
        for a in carnatic.models.RaagaAlias.objects.all():
            isdel = request.POST.get("alias-rm-%s" % a.id)
            if isdel is not None:
                a.delete()

        # Add new raaga
        refresh = False
        newraaga = request.POST.get("newname")
        if newraaga is not None and newraaga != "":
            refresh = True
            carnatic.models.Raaga.objects.create(name=newraaga)
        # Delete raaga
        for r in raagas:
            isdel = request.POST.get("delete-item-%s" % r.id)
            if isdel is not None:
                refresh = True
                r.delete()
        if refresh:
            raagas = carnatic.models.Raaga.objects.all()
            ret["items"] = raagas
    else:
        newraaga = request.GET.get("newname")
        if newraaga:
            ret["newname"] = newraaga

    return render(request, 'dashboard/raagataala.html', ret)

@login_required
def taalas(request):
    taalas = carnatic.models.Taala.objects.all()
    ret = {"items": taalas,
           "entityn": "Taala",
           "entitynpl": "Taalas",
           "entityurl": "dashboard-taalas",
           }
    if request.method == 'POST':
        # Add aliases
        for t in taalas:
            isadd = request.POST.get("item-%s-alias" % t.id)
            if isadd is not None:
                carnatic.models.TaalaAlias.objects.create(taala=t, name=isadd)
        # Delete alias
        for a in carnatic.models.TaalaAlias.objects.all():
            isdel = request.POST.get("alias-rm-%s" % a.id)
            if isdel is not None:
                a.delete()

        # Add new taala
        refresh = False
        newtaala = request.POST.get("newname")
        if newtaala is not None and newtaala != "":
            refresh = True
            carnatic.models.Taala.objects.create(name=newtaala)
        # Delete taala
        for t in taalas:
            isdel = request.POST.get("delete-item-%s" % t.id)
            if isdel is not None:
                refresh = True
                t.delete()
        if refresh:
            taalas = carnatic.models.Taala.objects.all()
            ret["items"] = taalas
    else:
        newtaala = request.GET.get("newname")
        if newtaala:
            ret["newname"] = newtaala

    return render(request, 'dashboard/raagataala.html', ret)

@login_required
def instruments(request):

    instruments = carnatic.models.Instrument.objects.all()

    ret = {"items": instruments,
           "entityn": "Instrument",
           "entitynpl": "Instruments",
           "entityurl": "dashboard-instruments",
           }
    if request.method == 'POST':
        # Add aliases
        for i in instruments:
            isadd = request.POST.get("item-%s-alias" % i.id)
            if isadd is not None:
                carnatic.models.InstrumentAlias.objects.create(instrument=i, name=isadd)
        # Delete alias
        for a in carnatic.models.InstrumentAlias.objects.all():
            isdel = request.POST.get("alias-rm-%s" % a.id)
            if isdel is not None:
                a.delete()

        # Add new instrument
        refresh = False
        newinstrument = request.POST.get("newname")
        if newinstrument is not None and newinstrument != "":
            refresh = True
            carnatic.models.Instrument.objects.create(name=newinstrument)
        # Delete instrument
        for i in instruments:
            isdel = request.POST.get("delete-item-%s" % i.id)
            if isdel is not None:
                refresh = True
                i.delete()
        if refresh:
            instruments = carnatic.models.Instrument.objects.all()
            ret["items"] = instruments
    else:
        newinstrument = request.GET.get("newname")
        if newinstrument:
            ret["newname"] = newinstrument

    return render(request, 'dashboard/raagataala.html', ret)
