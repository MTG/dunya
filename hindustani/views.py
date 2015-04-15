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

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
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

def main(request):
    qartist = []
    qinstr = []
    qraag = []
    qtaal = []
    qrelease = []
    qform = []
    qlaya = []

    if len(request.GET) == 0:
        # We have a 'default' query. If there's no other query we pre-seed it
        # Bhimsen Joshi
        qartist = [126]
        # Miya Malhar raag
        qraag = [147]
        return redirect("%s?a=126&g=147" % reverse('hindustani-main'))

    if "a" in request.GET:
        for i in request.GET.getlist("a"):
            qartist.append(int(i))
    if "i" in request.GET:
        for i in request.GET.getlist("i"):
            qinstr.append(int(i))
    if "r" in request.GET:
        for i in request.GET.getlist("r"):
            qrelease.append(int(i))
    if "g" in request.GET:
        for i in request.GET.getlist("g"):
            qraag.append(int(i))
    if "t" in request.GET:
        for i in request.GET.getlist("t"):
            qtaal.append(int(i))
    if "l" in request.GET:
        for i in request.GET.getlist("l"):
            qlaya.append(int(i))
    if "f" in request.GET:
        for i in request.GET.getlist("f"):
            qform.append(int(i))
    if "q" in request.GET:
        query = request.GET.get("q")
    else:
        query = None

    numartists = models.Artist.objects.filter(dummy=False).count()
    numcomposers = models.Composer.objects.count()
    numraags = models.Raag.objects.count()
    numtaals = models.Taal.objects.count()
    numreleases = models.Release.objects.count()
    numinstruments = models.Instrument.objects.filter(hidden=False).count()
    numworks = models.Work.objects.count()
    numforms = models.Form.objects.count()
    numlayas = models.Laya.objects.count()

    displayres = []
    querybrowse = False
    searcherror = False

    if qartist:
        raags = None
        if qraag:
            raags = [models.Raag.objects.get(pk=r) for r in qraag]
        taals = None
        if qtaal:
            taals = [models.Taal.objects.get(pk=t) for t in qtaal]
        forms = None
        if qform:
            forms = [models.Form.objects.get(pk=f) for f in qform]

        allartists = []
        for a in qartist:
            try:
                artist = models.Artist.objects.get(pk=a)
                allartists.append(artist)
                displayres.extend(artist.related_items())
            except models.Artist.DoesNotExist:
                pass

        thea = allartists[0]
        if len(allartists) > 1:
            othera = allartists[1:]
        else:
            othera = None
        displayres.extend(thea.combined_related_items(artists=othera, raags=raags, taals=taals, forms=forms))

    elif qinstr:
        for i in qinstr:
            try:
                instrument = models.Instrument.objects.get(pk=i)
                displayres.extend(instrument.related_items())
            except models.Instrument.DoesNotExist:
                pass
    elif qraag:
        forms = None
        if qform:
            forms = [models.Form.objects.get(pk=f) for f in qform]
        instrs = None
        if qinstr:
            instrs = [models.Instrument.objects.get(pk=i) for i in qinstr]
        for r in qraag:
            try:
                raag = models.Raag.objects.get(pk=r)
                displayres.extend(raag.related_items(instruments=instrs, forms=forms))
            except models.Raag.DoesNotExist:
                pass
    elif qtaal:
        forms = None
        if qform:
            forms = [models.Form.objects.get(pk=f) for f in qform]
        instrs = None
        if qinstr:
            instrs = [models.Instrument.objects.get(pk=i) for i in qinstr]
        layas = None
        if qlaya:
            layas = [models.Laya.objects.get(pk=l) for l in qlaya]
        for t in qtaal:
            try:
                taal = models.Taal.objects.get(pk=t)
                displayres.extend(taal.related_items(layas=layas, instruments=instrs, forms=forms))
            except models.Taal.objects.DoesNotExist:
                pass
    elif qrelease:
        for r in qrelease:
            try:
                release = models.Release.objects.with_user_access(request.user).get(pk=r)
                displayres.extend(release.related_items())
            except models.Release.DoesNotExist:
                pass

    elif qform:
        layas = None
        if qlaya:
            layas = [models.Laya.objects.get(pk=l) for l in qlaya]
        for f in qform:
            form = models.Form.objects.get(pk=f)
            displayres.extend(form.related_items(layas=layas))

    if query:
        try:
            results = search.search(query)
        except pysolr.SolrError:
            searcherror = True
            results = {}
        artists = results.get("artist", [])
        instruments = results.get("instrument", [])
        releases = results.get("release", [])
        raags = results.get("raag", [])
        taals = results.get("taal", [])
        forms = results.get("form", [])
        layas = results.get("laya", [])

        for a in artists:
            displayres.append(("artist", a))
        for i in instruments:
            displayres.append(("instrument", i))
        for c in releases:
            displayres.append(("release", c))
        for r in raags:
            displayres.append(("raag", r))
        for t in taals:
            displayres.append(("taal", t))
        for f in forms:
            displayres.append(("form", f))
        for l in layas:
            displayres.append(("laya", l))

        numartists = len(artists)
        numraags = len(raags)
        numtaals = len(taals)
        numreleases = len(releases)
        numinstruments = len(instruments)
        numforms = len(forms)
        numlayas = len(layas)
        results = True

    if displayres:
        numartists = len([i for i in displayres if i[0] == "artist"])
        numraags = len([i for i in displayres if i[0] == "raag"])
        numtaals = len([i for i in displayres if i[0] == "taal"])
        numreleases = len([i for i in displayres if i[0] == "release"])
        numinstruments = len([i for i in displayres if i[0] == "instrument"])
        numforms = len([i for i in displayres if i[0] == "form"])
        numlayas = len([i for i in displayres if i[0] == "laya"])
    
    print displayres

    ret = {"numartists": numartists,
           "filter_items": json.dumps(get_filter_items()),
           "numcomposers": numcomposers,
           "numraags": numraags,
           "numtaals": numtaals,
           "numreleases": numreleases,
           "numworks": numworks,
           "numinstruments": numinstruments,
           "numforms": numforms,
           "numlayas": numlayas,

           "results": displayres,

           "querytext": query,
           "querybrowse": querybrowse,
           "qartist": json.dumps(qartist),
           "qinstr": json.dumps(qinstr),
           "qraag": json.dumps(qraag),
           "qtaal": json.dumps(qtaal),
           "qlaya": json.dumps(qlaya),
           "qform": json.dumps(qform),
           "qrelease": json.dumps(qrelease),
           "searcherror": searcherror
           }

    return render(request, "hindustani/index.html", ret)

def composer(request, uuid, name=None):
    composer = get_object_or_404(models.Composer, mbid=uuid)

    works = composer.works.all()
    # We show all compositions, ordered by number of recordings
    works = sorted(works, key=lambda w: w.recording_set.count(), reverse=True)

    musicbrainz = composer.get_musicbrainz_url()
    w = data.models.SourceName.objects.get(name="Wikipedia")
    wikipedia = None
    wr = composer.references.filter(hindustani_composer_source_set=w)
    if wr.count():
        wikipedia = wr[0].uri
    desc = composer.description
    if desc and desc.source.source_name == w:
        wikipedia = composer.description.source.uri
    wr = composer.references.filter(source_name=w)
    if wr.count() and not wikipedia:
        wikipedia = wr[0].uri

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
    releases = models.Release.objects.with_user_access(request.user).order_by('title')
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

def recording(request, uuid, title=None):
    recording = get_object_or_404(models.Recording, mbid=uuid)

    try:
        wave = docserver.util.docserver_get_url(recording.mbid, "audioimages", "waveform32", 1, version=settings.FEAT_VERSION_IMAGE)
    except docserver.util.NoFileException:
        wave = None
    try:
        spec = docserver.util.docserver_get_url(recording.mbid, "audioimages", "spectrum32", 1, version=settings.FEAT_VERSION_IMAGE)
    except docserver.util.NoFileException:
        spec = None
    try:
        small = docserver.util.docserver_get_url(recording.mbid, "audioimages", "smallfull", version=settings.FEAT_VERSION_IMAGE)
    except docserver.util.NoFileException:
        small = None
    try:
        audio = docserver.util.docserver_get_mp3_url(recording.mbid)
    except docserver.util.NoFileException:
        audio = None
    try:
        tonic = docserver.util.docserver_get_contents(recording.mbid, "votedtonic", "tonic", version=settings.FEAT_VERSION_TONIC)
        notenames = ["A", "A♯", "B", "C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯"]
        tonic = round(float(tonic), 2)
        thebin = (12 * math.log(tonic / 440.0) / math.log(2)) % 12
        thebin = int(round(thebin))
        tonic = str(tonic)
        if thebin <= 11 and thebin >= 0:
            tonicname = notenames[thebin]
        else:
            print "bin is", thebin, "weird"
            print tonic
            tonicname = ""
    except docserver.util.NoFileException:
        tonic = None
        tonicname = None

    vilambit = models.Laya.Vilambit
    drawtempo = not recording.layas.filter(pk=vilambit.pk).exists()
    if drawtempo:
        try:
            aksharaurl = docserver.util.docserver_get_url(recording.mbid, "rhythm", "APcurve", version=settings.FEAT_VERSION_RHYTHM)
            akshara = docserver.util.docserver_get_contents(recording.mbid, "rhythm", "aksharaPeriod", version=settings.FEAT_VERSION_RHYTHM)
            akshara = str(round(float(akshara), 3) * 1000)
        except docserver.util.NoFileException:
            akshara = None
            aksharaurl = None
    else:
        akshara = None
        aksharaurl = None

    try:
        pitchtrackurl = docserver.util.docserver_get_url(recording.mbid, "normalisedpitch", "packedpitch", version=settings.FEAT_VERSION_NORMALISED_PITCH)
        histogramurl = docserver.util.docserver_get_url(recording.mbid, "normalisedpitch", "drawhistogram", version=settings.FEAT_VERSION_NORMALISED_PITCH)
        rhythmurl = docserver.util.docserver_get_url(recording.mbid, "rhythm", "aksharaTicks", version=settings.FEAT_VERSION_RHYTHM)
    except docserver.util.NoFileException:
        pitchtrackurl = None
        histogramurl = None
        rhythmurl = None

    try:
        release = recording.release_set.get()
        recordings = list(release.recordings.all())
        recordingpos = recordings.index(recording)
    except models.Release.DoesNotExist:
        release = None
        recordings = []
        recordingpos = 0
    nextrecording = None
    prevrecording = None
    if recordingpos > 0:
        prevrecording = recordings[recordingpos - 1]
    if recordingpos + 1 < len(recordings):
        nextrecording = recordings[recordingpos + 1]
    mbid = recording.mbid

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
           "release": release,
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
