# -*- coding: UTF-8 -*-

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

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings

import json
import math
import random

import pysolr

import data
from hindustani import models
from hindustani import search
import docserver

def get_filter_items():
    filter_items = [
        models.Artist.get_filter_criteria(),
        models.Release.get_filter_criteria(),
        models.Instrument.get_filter_criteria(),
        models.Raag.get_filter_criteria(),
        models.Taal.get_filter_criteria(),
        models.Laya.get_filter_criteria(),
        models.Form.get_filter_criteria()
    ]
    return filter_items

def searchcomplete(request):
    # TODO: Hindustani-specific search
    term = request.GET.get("term")
    ret = []
    error = False
    if term:
        try:
            suggestions = search.autocomplete(term)
            ret = [{"id": i, "label": l, "value": l} for i, l in enumerate(suggestions, 1)]
        except pysolr.SolrError:
            error = True
    return HttpResponse(json.dumps(ret), content_type="application/json")

def searchcomplete(request):
    term = request.GET.get("input")
    ret = []
    if term:
        suggestions = models.Release.objects.filter(title__istartswith=term)[:3]
        ret = [{"id": i, "category": "release", "name": l.title, 'mbid': str(l.mbid)} for i, l in enumerate(suggestions, 1)]
        suggestions = models.Artist.objects.filter(name__istartswith=term)[:3]
        ret += [{"id": i, "category": "artist", "name": l.name, 'mbid': str(l.mbid)} for i, l in enumerate(suggestions, len(ret))]
    return HttpResponse(json.dumps(ret), content_type="application/json")

def recordings_search(request):
    q = request.GET.get('recording', '')

    s_artists = request.GET.get('artists', '')
    s_releases = request.GET.get('releases', '')
    s_instruments = request.GET.get('instruments', '')
    s_rags = request.GET.get('rags', '')
    s_tals = request.GET.get('tals', '')

    recordings = models.Recording.objects
    if s_artists != '' or s_releases != '' or q\
            or s_instruments != '' or s_rags != '' or s_tals != '':
        if q and q!='':
            ids = list(models.Work.objects.filter(title__unaccent__icontains=q).values_list('pk', flat=True))
            recordings = recordings.filter(works__id__in=ids)\
                    | recordings.filter(title__unaccent__icontains=q)\
                    | recordings.filter(release__title__unaccent__icontains=q)

        if s_artists and s_artists != '':
            artists = s_artists.split()
            recordings = recordings.filter(works__composers__mbid__in=artists)\
                    | recordings.filter(works__lyricists__mbid__in=artists)\
                    | recordings.filter(release__artists__mbid__in=artists)

        if s_releases and s_releases != '':
            recordings = recordings.filter(releases__mbid__in=s_releases.split())

        if s_instruments and s_instruments != '':
            recordings = recordings.filter(instrumentperformance__instrument__mbid__in=s_instruments.split())

        if s_rags and s_rags != '':
            recordings = recordings.filter(raags__uuid__in=s_rags.split())

        if s_tals and s_tals != '':
            recordings = recordings.filter(taals__uuid__in=s_tals.split())


    paginator = Paginator(recordings.all(), 25)
    page = request.GET.get('page')
    next_page = None
    try:
        recordings = paginator.page(page)
        if recordings.has_next():
            next_page = recordings.next_page_number()
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        recordings = paginator.page(1)
        if recordings.has_next():
            next_page = recordings.next_page_number()
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        recordings = paginator.page(paginator.num_pages)
    results = {
            "results": [item.get_dict() for item in recordings.object_list],
            "moreResults": next_page
    }
    return HttpResponse(json.dumps(results), content_type='application/json')


def filters(request):

    taals = models.Taal.objects.prefetch_related('aliases').all()
    taallist = []
    for r in taals:
        taallist.append({"name": r.name, "uuid": str(r.uuid), "aliases": [a.name for a in r.aliases.all()]})

    raags = models.Raag.objects.prefetch_related('aliases').all()
    raaglist = []
    for r in raags:
        raaglist.append({"name": r.name, "uuid": str(r.uuid), "aliases": [a.name for a in r.aliases.all()]})

    releases = models.Release.objects.all()
    releaselist = []
    for r in releases:
        releaselist.append({"name": r.title, "mbid": str(r.mbid)})

    artists = models.Artist.objects.all()
    artistlist = []
    for a in artists:
        rr = []
        tt = []
        cc = []
        ii = []

        artistlist.append({"name": a.name, "mbid": str(a.mbid), "concerts": [str(c.mbid) for c in cc], "raagas": [str(r.uuid) for r in rr], "taalas": [str(t.uuid) for t in tt], "instruments": [str(i.mbid) for i in ii]})


    instruments = models.Instrument.objects.all()
    instrumentlist = []
    for i in instruments:
        instrumentlist.append({"name": i.name, "mbid": str(i.mbid)})


    ret = {"artists": artistlist,
           "releases": releaselist,
           "instruments": instrumentlist,
           u"rags": raaglist,
           u"tals": taallist,
           }

    return JsonResponse(ret)

def main(request):
    return render(request, "hindustani/index.html")

def composer(request, uuid, name=None):
    composer = get_object_or_404(models.Composer, mbid=uuid)

    works = composer.works.all()
    # We show all compositions, ordered by number of recordings
    works = sorted(works, key=lambda w: w.recording_set.count(), reverse=True)

    musicbrainz = composer.get_musicbrainz_url()
    w = data.models.SourceName.objects.get(name="Wikipedia")
    wikipedia = None
    desc = composer.description
    if desc and desc.source.source_name == w:
        wikipedia = composer.description.source.uri

    ret = {"composer": composer,
           "mb": musicbrainz,
           "wiki": wikipedia,
           "works": works}

    return render(request, "hindustani/composer.html", ret)

def artistsearch(request):
    artists = models.Artist.objects.filter(dummy=False).order_by('name')
    ret = []
    for a in artists:
        ret.append({"id": a.id, "name": a.name})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def artist(request, uuid, name=None):
    artist = get_object_or_404(models.Artist, mbid=uuid)

    musicbrainz = artist.get_musicbrainz_url()
    w = data.models.SourceName.objects.get(name="Wikipedia")
    wikipedia = None
    desc = artist.description
    if desc and desc.source.source_name == w:
        wikipedia = artist.description.source.uri

    # Sample is the first track of any of their releases (Vignesh, Dec 9)
    releases = artist.releases()
    sample = None
    if releases:
        recordings = releases[0].recordings.all()
        if recordings:
            sample = recordings[0]

    ret = {"artist": artist,
           "mb": musicbrainz,
           "wiki": wikipedia,
           "sample": sample
           }
    return render(request, "hindustani/artist.html", ret)

def releasesearch(request):
    permission = data.utils.get_user_permissions(request.user)
    releases = models.Release.objects.with_permissions(False, permission).order_by('title')
    ret = []
    for r in releases:
        ret.append({"id": r.id, "title": r.title})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def release(request, uuid, title=None):
    release = get_object_or_404(models.Release, mbid=uuid)
    similar = release.get_similar()

    ret = {"release": release,
           "similar": similar
           }
    return render(request, "hindustani/release.html", ret)

def recordingbyid(request, recordingid, title=None):
    recording = get_object_or_404(models.Recording, pk=recordingid)
    return redirect(recording.get_absolute_url(), permanent=True)


def recording(request, uuid, title=None):
    recording = get_object_or_404(models.Recording, mbid=uuid)

    try:
        wave = docserver.util.docserver_get_url(recording.mbid, "audioimages", "waveform32", 1, version=settings.FEAT_VERSION_IMAGE)
    except docserver.exceptions.NoFileException:
        wave = None
    try:
        spec = docserver.util.docserver_get_url(recording.mbid, "audioimages", "spectrum32", 1, version=settings.FEAT_VERSION_IMAGE)
    except docserver.exceptions.NoFileException:
        spec = None
    try:
        small = docserver.util.docserver_get_url(recording.mbid, "audioimages", "smallfull", version=settings.FEAT_VERSION_IMAGE)
    except docserver.exceptions.NoFileException:
        small = None
    try:
        audio = docserver.util.docserver_get_mp3_url(recording.mbid)
    except docserver.exceptions.NoFileException:
        audio = None
    try:
        tonic = docserver.util.docserver_get_contents(recording.mbid, "hindustanivotedtonic", "tonic", version=settings.FEAT_VERSION_TONIC)
        notenames = ["A", "A♯", "B", "C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯"]
        tonic = round(float(tonic), 2)
        thebin = (12 * math.log(tonic / 440.0) / math.log(2)) % 12
        thebin = int(round(thebin))
        tonic = str(tonic)
        if thebin <= 11 and thebin >= 0:
            tonicname = notenames[thebin]
        else:
            tonicname = ""
    except docserver.exceptions.NoFileException:
        tonic = None
        tonicname = None

    vilambit = models.Laya.Vilambit
    drawtempo = not recording.layas.filter(pk=vilambit.pk).exists()
    if drawtempo:
        try:
            aksharaurl = docserver.util.docserver_get_url(recording.mbid, "rhythm", "APcurve", version=settings.FEAT_VERSION_RHYTHM)
            akshara = docserver.util.docserver_get_contents(recording.mbid, "rhythm", "aksharaPeriod", version=settings.FEAT_VERSION_RHYTHM)
            akshara = str(round(float(akshara), 3) * 1000)
        except docserver.exceptions.NoFileException:
            akshara = None
            aksharaurl = None
    else:
        akshara = None
        aksharaurl = None

    try:
        pitchtrackurl = docserver.util.docserver_get_url(recording.mbid, "hindustaninormalisedpitch", "packedpitch", version=settings.FEAT_VERSION_HINDUSTANI_NORMALISED_PITCH)
        histogramurl = docserver.util.docserver_get_url(recording.mbid, "hindustaninormalisedpitch", "drawhistogram", version=settings.FEAT_VERSION_HINDUSTANI_NORMALISED_PITCH)
        rhythmurl = docserver.util.docserver_get_url(recording.mbid, "rhythm", "aksharaTicks", version=settings.FEAT_VERSION_RHYTHM)
    except docserver.exceptions.NoFileException:
        pitchtrackurl = None
        histogramurl = None
        rhythmurl = None

    try:
        releases = recording.release_set.all()
        # TODO: If this recording is on more than 1 release, the position
        # might be that of a different release. How will we know?
        release = releases[0]
        recordings = list(release.recordings.all())
        recordingpos = recordings.index(recording)
    except models.Release.DoesNotExist:
        releases = []
        recordings = []
        recordingpos = 0
    nextrecording = None
    prevrecording = None
    if recordingpos > 0:
        prevrecording = recordings[recordingpos - 1]
    if recordingpos + 1 < len(recordings):
        nextrecording = recordings[recordingpos + 1]
    mbid = recording.mbid

    artists = list(set([v for s in [r.artistnames() for r in releases] for v in s]))

    ret = {"recording": recording,
           "objecttype": "recording",
           "objectid": recording.id,
           "waveform": wave,
           "spectrogram": spec,
           "smallimage": small,
           "audio": audio,
           "tonic": tonic,
           "tonicname": tonicname,
           "akshara": akshara,
           "mbid": mbid,
           "nextrecording": nextrecording,
           "prevrecording": prevrecording,
           "pitchtrackurl": pitchtrackurl,
           "histogramurl": histogramurl,
           "rhythmurl": rhythmurl,
           "aksharaurl": aksharaurl,
           "drawtempo": drawtempo,
           "releases": releases,
           "artists": artists
           }
    return render(request, "hindustani/recording.html", ret)

def work(request, uuid, title=None):
    work = get_object_or_404(models.Work, mbid=uuid)

    ret = {"work": work
           }
    return render(request, "hindustani/work.html", ret)

def layasearch(request):
    layas = models.Laya.objects.all().order_by('name')
    ret = []
    for l in layas:
        ret.append({"id": l.id, "name": str(l)})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def layabyid(request, layaid, name=None):
    laya = get_object_or_404(models.Laya, pk=layaid)
    return redirect(laya.get_absolute_url(), permanent=True)

def laya(request, uuid, name=None):
    laya = get_object_or_404(models.Laya, uuid=uuid)

    ret = {"laya": laya
           }
    return render(request, "hindustani/laya.html", ret)

def raagsearch(request):
    raags = models.Raag.objects.all().order_by('name')
    ret = []
    for r in raags:
        ret.append({"id": r.id, "name": str(r)})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def raagbyid(request, raagid, name=None):
    raag = get_object_or_404(models.Raag, pk=raagid)
    return redirect(raag.get_absolute_url(), permanent=True)

def raag(request, uuid, name=None):
    raag = get_object_or_404(models.Raag, uuid=uuid)
    recordings = raag.recording_set.all()
    sample = None
    if recordings.exists():
        sample = random.sample(recordings, 1)[0]

    ret = {"raag": raag,
           "sample": sample
           }
    return render(request, "hindustani/raag.html", ret)

def taalsearch(request):
    taals = models.Taal.objects.all().order_by('name')
    ret = []
    for t in taals:
        ret.append({"id": t.id, "name": str(t)})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def taalbyid(request, taalid, name=None):
    taal = get_object_or_404(models.Taal, pk=taalid)
    return redirect(taal.get_absolute_url(), permanent=True)

def taal(request, uuid, name=None):
    taal = get_object_or_404(models.Taal, uuid=uuid)

    """
    We display all the recordings of a taal and group them by
    layas. Currently, the vilambit laya should be the last group
    shown. Recordings that are associated with more than one laya
    are only shown once in their first group
    """
    # Retrieve the three Layas in Dunya
    dhrut = models.Laya.Dhrut
    madhya = models.Laya.Madhya
    vilambit = models.Laya.Vilambit

    recordings = taal.recording_set.all()
    recordings = []
    recordings.extend([r for r in recordings if r.layas.count() == 1 and dhrut in r.layas.all()][:5])
    recordings.extend([r for r in recordings if r.layas.count() == 1 and madhya in r.layas.all()][:5])
    recordings.extend([r for r in recordings if r.layas.count() == 1 and vilambit in r.layas.all()][:5])
    sample = None
    if recordings:
        sample = recordings[0]

    ret = {"taal": taal,
           "recordings": recordings,
           "sample": sample
           }
    return render(request, "hindustani/taal.html", ret)


def formsearch(request):
    forms = models.Form.objects.all().order_by('name')
    ret = []
    for l in forms:
        ret.append({"id": l.id, "name": str(l)})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def formbyid(request, formid, name=None):
    form = get_object_or_404(models.Form, pk=formid)
    return redirect(form.get_absolute_url(), permanent=True)

def form(request, uuid, name=None):
    form = get_object_or_404(models.Form, uuid=uuid)

    ret = {"form": form
           }
    return render(request, "hindustani/form.html", ret)

def instrumentsearch(request):
    instruments = models.Instrument.objects.filter(hidden=False).order_by('name')
    ret = []
    for l in instruments:
        ret.append({"id": l.id, "name": str(l)})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def instrumentbyid(request, instrumentid, name=None):
    instrument = get_object_or_404(models.Instrument, pk=instrumentid)
    return redirect(instrument.get_absolute_url(), permanent=True)

def instrument(request, uuid, name=None):
    instrument = get_object_or_404(models.Instrument, mbid=uuid, hidden=False)

    sample = None
    # Look for a release by an artist who plays this instrument and take
    # the first track
    releases = models.Release.objects.filter(artists__main_instrument=instrument)
    if releases.exists():
        sample = releases[0].recordings.all()[0]

    ret = {"instrument": instrument,
           "sample": sample
           }
    return render(request, "hindustani/instrument.html", ret)
