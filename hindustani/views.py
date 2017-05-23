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

def searchcomplete(request):
    term = request.GET.get("input")
    ret = []
    if term:
        suggestions = models.Release.objects.filter(title__istartswith=term)[:3]
        ret = [{"category": "releases", "name": l.title, 'mbid': str(l.mbid)} for i, l in enumerate(suggestions, 1)]
        suggestions = models.Artist.objects.filter(name__istartswith=term)[:3]
        ret += [{"category": "artists", "name": l.name, 'mbid': str(l.mbid)} for i, l in enumerate(suggestions, len(ret))]
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
            recordings = recordings.filter(release__mbid__in=s_releases.split())

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


