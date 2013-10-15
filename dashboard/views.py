from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import user_passes_test
import django.utils.timezone

from dashboard import models
from dashboard import forms
from dashboard import jobs
import docserver

import compmusic
import os
import importlib
import json

import carnatic

def is_staff(user):
    return user.is_staff

@user_passes_test(is_staff)
def index(request):
    if request.method == 'POST':
        form = forms.AddCollectionForm(request.POST)
        if form.is_valid():
            # Import collection id
            coll_id = form.cleaned_data['collectionid']
            path = form.cleaned_data['path']
            coll_name = form.cleaned_data['collectionname']
            do_import = form.cleaned_data['do_import']
            checkers = []
            for i in form.cleaned_data['checkers']:
                checkers.append(get_object_or_404(models.CompletenessChecker, pk=int(i)))
            new_collection = models.Collection.objects.create(id=coll_id, name=coll_name,
                                    root_directory=path, do_import=do_import)
            new_collection.checkers.add(*checkers) 
            docserver.models.Collection.objects.get_or_create(collectionid=coll_id, 
                    defaults={"root_directory":path, "name":coll_name})
            jobs.load_and_import_collection(new_collection.id)
            return HttpResponseRedirect(reverse('dashboard-home'))
    else:
        form = forms.AddCollectionForm()

    collections = models.Collection.objects.all()
    ret = {'form': form, 'collections': collections}
    return render(request, 'dashboard/index.html', ret)

@user_passes_test(is_staff)
def collection(request, uuid):
    c = get_object_or_404(models.Collection, pk=uuid)

    rescan = request.GET.get("rescan")
    if rescan is not None:
        jobs.load_and_import_collection(c.id)
        return HttpResponseRedirect(reverse('dashboard.views.collection', args=[uuid]))
    order = request.GET.get("order")

    releases = models.MusicbrainzRelease.objects.filter(collection=c)
    if order == "date":
        def sortkey(rel):
            return rel.get_current_state().state_date
    elif order == "unmatched":
        def sortkey(rel):
            return (False if rel.matched_paths() else True, rel.get_current_state().state_date)
    elif order == "ignored":
        def sortkey(rel):
            return rel.ignore
    elif order == "error":
        def sortkey(rel):
            count = 0
            for state in rel.get_latest_checker_results():
                if state.result == 'b':
                    count += 1
            for directory in rel.collectiondirectory_set.all():
                for f in directory.collectionfile_set.all():
                    for state in f.get_latest_checker_results():
                        if state.result == 'b':
                            count += 1
            return count
    else:
        def sortkey(obj):
            pass
    releases = sorted(releases, key=sortkey, reverse=True)

    numfinished = sum(1 for _ in (r for r in releases if r.get_current_state().state == 'f'))
    numtotal = sum(1 for _ in (r for r in releases if len(r.all_files())))

    folders = models.CollectionDirectory.objects.filter(collection=c, musicbrainzrelease__isnull=True)
    log = models.CollectionLogMessage.objects.filter(collection=c).order_by('-datetime')
    ret = {"collection": c, "log_messages": log, "releases": releases, "folders": folders, \
            "numtotal": numtotal, "numfinished": numfinished}
    return render(request, 'dashboard/collection.html', ret)

@user_passes_test(is_staff)
def release(request, releaseid):
    release = get_object_or_404(models.MusicbrainzRelease, pk=releaseid)

    reimport = request.GET.get("reimport")
    if reimport is not None:
        jobs.import_release.delay(release.id)
        return HttpResponseRedirect(reverse('dashboard.views.release', args=[releaseid]))

    ignore = request.GET.get("ignore")
    if ignore is not None:
        release.ignore = True
        release.save()
        return HttpResponseRedirect(reverse('dashboard.views.release', args=[releaseid]))
    unignore = request.GET.get("unignore")
    if unignore is not None:
        release.ignore = False
        release.save()
        return HttpResponseRedirect(reverse('dashboard.views.release', args=[releaseid]))

    files = release.collectiondirectory_set.order_by('path').all()
    log = release.musicbrainzreleaselogmessage_set.order_by('-datetime').all()

    allres = []
    results = release.get_latest_checker_results()
    for r in results:
        allres.append({"latest": r,
                       "others": release.get_rest_results_for_checker(r.checker.id)
                      })

    ret = {"release": release, "files": files, "results": allres, "log_messages": log}
    return render(request, 'dashboard/release.html', ret)

@user_passes_test(is_staff)
def file(request, fileid):
    thefile = get_object_or_404(models.CollectionFile, pk=fileid)
    log = thefile.collectionfilelogmessage_set.order_by('-datetime').all()

    allres = []
    results = thefile.get_latest_checker_results()
    for r in results:
        allres.append({"latest": r,
                       "others": thefile.get_rest_results_for_checker(r.checker.id)
                      })

    collection = thefile.directory.collection
    docid = thefile.recordingid
    docsrvcoll = docserver.models.Collection.objects.get(collectionid=collection.id)
    sourcefiles = []
    derivedfiles = []
    docsrvdoc = None
    try:
        docsrvdoc = docsrvcoll.documents.get(external_identifier=docid)
        sourcefiles = docsrvdoc.sourcefiles.all()
        derivedfiles = docsrvdoc.derivedfiles.all()
    except docserver.models.Document.DoesNotExist:
        pass
    ret = {"file": thefile,
            "results": allres,
            "log_messages": log,
            "sourcefiles": sourcefiles,
            "derivedfiles": derivedfiles,
            "docsrvdoc": docsrvdoc}
    return render(request, 'dashboard/file.html', ret)

@user_passes_test(is_staff)
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
        return HttpResponseRedirect(reverse('dashboard.views.directory', args=[dirid]))

    collection = directory.collection
    full_path = os.path.join(collection.root_directory, directory.path)
    files = os.listdir(full_path)
    meta = {}
    releaseids = set()
    releasename = set()
    artistids = set()
    artistname = set()
    for f in files:
        fname = os.path.join(full_path, f)
        if compmusic.is_mp3_file(fname):
            data = compmusic.file_metadata(fname)
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

@user_passes_test(is_staff)
def raagas(request):
    # TODO: Raaga/taala/instrument is all duplicated code!
    raagas = carnatic.models.Raaga.objects.all()
    ret = {"items": raagas,
           "entityn": "Raaga",
           "entitynpl": "Raagas",
           "entityurl": "dashboard-raagas",
           "title": "Raaga editor"
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

@user_passes_test(is_staff)
def taalas(request):
    taalas = carnatic.models.Taala.objects.all()
    ret = {"items": taalas,
           "entityn": "Taala",
           "entitynpl": "Taalas",
           "entityurl": "dashboard-taalas",
           "title": "Taala editor"
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

@user_passes_test(is_staff)
def instruments(request):

    instruments = carnatic.models.Instrument.objects.all()

    ret = {"items": instruments,
           "entityn": "Instrument",
           "entitynpl": "Instruments",
           "entityurl": "dashboard-instruments",
           "title": "Instrument editor"
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
