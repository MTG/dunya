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

import json
import math

import pysolr

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
        # special case, we have this so we can put a ? in the arglist
        # but it's actually a browse
        if query == "1":
            print "query is none"
            query = None
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
        for a in qartist:
            print "doing artist", a
            try:
                artist = models.Artist.objects.get(pk=a)
                displayres.extend(artist.related_items())
            except models.Artist.DoesNotExist:
                pass
    if qinstr:
        for i in qinstr:
            try:
                instrument = models.Instrument.objects.get(pk=i)
                displayres.extend(instrument.related_items())
            except models.Instrument.DoesNotExist:
                pass
    if qraag:
        for r in qraag:
            try:
                raag = models.Raag.objects.get(pk=r)
                displayres.extend(raag.related_items())
            except models.Raag.DoesNotExist:
                pass
    if qtaal:
        for t in qtaal:
            try:
                taal = models.Taal.objects.get(pk=t)
                displayres.extend(taal.related_items())
            except models.Taal.objects.DoesNotExist:
                pass
    if qrelease:
        for r in qrelease:
            try:
                release = models.Release.objects.get(pk=r)
                displayres.extend(release.related_items())
            except models.Release.DoesNotExist:
                pass
    layas = models.Laya.objects.filter(pk__in=qlaya)
    [ displayres.extend(l.related_items()) for l in layas ]

    forms = models.Form.objects.filter(pk__in=qform)
    [ displayres.extend(f.related_items()) for f in forms ]

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
        laya = results.get("laya", [])

        displayres = []
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
           "qrelease": json.dumps(qrelease),
           "searcherror": searcherror
           }

    return render(request, "hindustani/index.html", ret)

def composer(request, uuid):
    composer = get_object_or_404(models.Composer, mbid=uuid)

    ret = {"composer": composer
          }
    return render(request, "hindustani/composer.html", ret)

def artistsearch(request):
    artists = models.Artist.objects.filter(dummy=False).order_by('name')
    ret = []
    for a in artists:
        ret.append({"id": a.id, "name": a.name})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def artist(request, uuid):
    artist = get_object_or_404(models.Artist, mbid=uuid)

    ret = {"artist": artist
          }
    return render(request, "hindustani/artist.html", ret)

def releasesearch(request):
    releases = models.Release.objects.order_by('title')
    ret = []
    for r in releases:
        ret.append({"id": r.id, "title": r.title})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def release(request, uuid):
    release = get_object_or_404(models.Release, mbid=uuid)
    similar = release.get_similar()

    ret = {"release": release,
            "similar": similar
          }
    return render(request, "hindustani/release.html", ret)

def recording(request, uuid):
    recording = get_object_or_404(models.Recording, mbid=uuid)

    try:
        wave = docserver.util.docserver_get_url(recording.mbid, "audioimages", "waveform32", 1)
    except docserver.util.NoFileException:
        wave = None
    try:
        spec = docserver.util.docserver_get_url(recording.mbid, "audioimages", "spectrum32", 1)
    except docserver.util.NoFileException:
        spec = None
    try:
        small = docserver.util.docserver_get_url(recording.mbid, "audioimages", "smallfull")
    except docserver.util.NoFileException:
        small = None
    try:
        audio = docserver.util.docserver_get_mp3_url(recording.mbid)
    except docserver.util.NoFileException:
        audio = None
    try:
        tonic = docserver.util.docserver_get_contents(recording.mbid, "ctonic", "tonic")
        notenames = ["A", "A♯", "B", "C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯"]
        tonic = round(float(tonic), 2)
        thebin = (12 * math.log(tonic/440.0) / math.log(2)) % 12
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
            aksharaurl = docserver.util.docserver_get_url(recording.mbid, "rhythm", "APcurve")
            akshara = docserver.util.docserver_get_contents(recording.mbid, "rhythm", "aksharaPeriod")
            akshara = str(round(float(akshara), 3) * 1000)
        except docserver.util.NoFileException:
            akshara = None
            aksharaurl = None
    else:
        akshara = None
        aksharaurl = None

    try:
        pitchtrackurl = docserver.util.docserver_get_url(recording.mbid, "normalisedpitch", "packedpitch")
        histogramurl = docserver.util.docserver_get_url(recording.mbid, "normalisedpitch", "drawhistogram")
        rhythmurl = docserver.util.docserver_get_url(recording.mbid, "rhythm", "aksharaTicks")
    except docserver.util.NoFileException:
        pitchtrackurl = None
        histogramurl = None
        rhythmurl = None

    try:
        release = recording.release_set.get()
        tracks = list(release.tracks.all())
        recordingpos = tracks.index(recording)
    except models.Release.DoesNotExist:
        release = None
        tracks = []
        recordingpos = 0
    nextrecording = None
    prevrecording = None
    if recordingpos > 0:
        prevrecording = tracks[recordingpos-1]
    if recordingpos+1 < len(tracks):
        nextrecording = tracks[recordingpos+1]
    mbid = recording.mbid

    ret = { "recording": recording,
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

def work(request, uuid):
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

def laya(request, layaid):
    laya = get_object_or_404(models.Laya, pk=layaid)

    ret = {"laya": laya
          }
    return render(request, "hindustani/laya.html", ret)

def raagsearch(request):
    raags = models.Raag.objects.all().order_by('name')
    ret = []
    for r in raags:
        ret.append({"id": r.id, "name": str(r)})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def raag(request, raagid):
    raag = get_object_or_404(models.Raag, pk=raagid)

    ret = {"raag": raag
          }
    return render(request, "hindustani/raag.html", ret)

def taalsearch(request):
    taals = models.Taal.objects.all().order_by('name')
    ret = []
    for t in taals:
        ret.append({"id": t.id, "name": str(t)})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def taal(request, taalid):
    taal = get_object_or_404(models.Taal, pk=taalid)

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
    
    def laya_ordering(recording):
        """
        A helper function passed as key to the sorting function
        Depending on the recording's layas, the following is returned:
            1-> if it has dhrut
            2-> if it has madhya
            3-> if it only has vilambit
        """
        layas = recording.layas.all()
        if dhrut in layas:
            return 1
        elif madhya in layas:
            return 2
        elif vilambit in layas:
            return 3
        else:
            return 999
    recordings = taal.recording_set.all()
    tracks = sorted(recordings, key=laya_ordering) 
    sample = None
    if tracks:
        sample = tracks[0]
    
    ret = { "taal": taal,
            "tracks": tracks,
            "sample": sample
          }
    return render(request, "hindustani/taal.html", ret)


def formsearch(request):
    forms = models.Form.objects.all().order_by('name')
    ret = []
    for l in forms:
        ret.append({"id": l.id, "name": str(l)})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def form(request, formid):
    form = get_object_or_404(models.Form, pk=formid)

    ret = {"form": form
          }
    return render(request, "hindustani/form.html", ret)

def instrumentsearch(request):
    instruments = models.Instrument.objects.filter(hidden=False).order_by('name')
    ret = []
    for l in instruments:
        ret.append({"id": l.id, "name": str(l)})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def instrument(request, instrumentid):
    instrument = get_object_or_404(models.Instrument, pk=instrumentid)

    ret = {"instrument": instrument
          }
    return render(request, "hindustani/instrument.html", ret)

