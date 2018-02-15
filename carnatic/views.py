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

import json
import math

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

import dashboard.models
import dashboard.views
import docserver
import docserver.exceptions
import docserver.util
from carnatic.models import *
from data import utils


def searchcomplete(request):
    term = request.GET.get("input")
    ret = []
    if term:
        suggestions = Concert.objects.filter(title__istartswith=term)[:3]
        ret = [{"category": "concerts", "name": l.title, 'mbid': str(l.mbid)} for i, l in enumerate(suggestions, 1)]
        suggestions = Artist.objects.filter(name__istartswith=term)[:3]
        ret += [{"category": "artists", "name": l.name, 'mbid': str(l.mbid)} for i, l in enumerate(suggestions, len(ret))]
    return HttpResponse(json.dumps(ret), content_type="application/json")


def recordings_search(request):
    q = request.GET.get('recording', '')

    s_artists = request.GET.get('artists', '')
    s_concerts = request.GET.get('concerts', '')
    s_instruments = request.GET.get('instruments', '')
    s_raga = request.GET.get('ragas', '')
    s_tala = request.GET.get('talas', '')

    recordings = Recording.objects
    if s_artists != '' or s_concerts != '' or q\
            or s_instruments != '' or s_raga != '' or s_tala != '':
        if q and q!='':
            ids = list(Work.objects.filter(title__unaccent__icontains=q).values_list('pk', flat=True))
            recordings = recordings.filter(works__id__in=ids)\
                    | recordings.filter(title__unaccent__icontains=q)\
                    | recordings.filter(concert__title__unaccent__icontains=q)

        if s_artists and s_artists != '':
            artists = s_artists.split()
            recordings = recordings.filter(works__composers__mbid__in=artists)\
                    | recordings.filter(works__lyricists__mbid__in=artists)\
                    | recordings.filter(concert__artists__mbid__in=artists)

        if s_concerts and s_concerts != '':
            recordings = recordings.filter(concert__mbid__in=s_concerts.split())

        if s_instruments and s_instruments != '':
            recordings = recordings.filter(instrumentperformance__instrument__mbid__in=s_instruments.split())

        if s_raga and s_raga != '':
            recordings = recordings.filter(works__raaga__uuid__in=s_raga.split())

        if s_tala and s_tala != '':
            recordings = recordings.filter(works__taala__uuid__in=s_tala.split())

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


def main(request):
    return render(request, "carnatic/index.html")


def filters(request):

    taalas = Taala.objects.prefetch_related('aliases').all()
    taalalist = []
    for r in taalas:
        taalalist.append({"name": r.name, "uuid": str(r.uuid), "aliases": [a.name for a in r.aliases.all()]})

    raagas = Raaga.objects.prefetch_related('aliases').all()
    raagalist = []
    for r in raagas:
        raagalist.append({"name": r.name, "uuid": str(r.uuid), "aliases": [a.name for a in r.aliases.all()]})

    concerts = Concert.objects.all()
    concertlist = []
    for c in concerts:
        concertlist.append({"name": c.title, "mbid": str(c.mbid)})

    artists = Artist.objects.all()
    artistlist = []
    for a in artists:
        rr = []
        tt = []
        cc = []
        ii = []

        artistlist.append({"name": a.name, "mbid": str(a.mbid), "concerts": [str(c.mbid) for c in cc], "raagas": [str(r.uuid) for r in rr], "taalas": [str(t.uuid) for t in tt], "instruments": [str(i.mbid) for i in ii]})

    instruments = Instrument.objects.all()
    instrumentlist = []
    for i in instruments:
        instrumentlist.append({"name": i.name, "mbid": str(i.mbid)})

    ret = {"artists": artistlist,
           "concerts": concertlist,
           "instruments": instrumentlist,
           u"ragas": raagalist,
           u"talas": taalalist,
           }

    return JsonResponse(ret)


def recordingbyid(request, recordingid, title=None):
    recording = get_object_or_404(Recording, pk=recordingid)
    return redirect(recording.get_absolute_url(), permanent=True)


def recording(request, uuid, title=None):
    recording = get_object_or_404(Recording, mbid=uuid)

    show_restricted = False
    if recording.is_restricted() and request.show_bootlegs:
        show_restricted = True
    elif recording.is_restricted() and not request.show_bootlegs:
        raise Http404

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
        tonic = docserver.util.docserver_get_contents(recording.mbid, "carnaticvotedtonic", "tonic", version=settings.FEAT_VERSION_TONIC)
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
    try:
        akshara = docserver.util.docserver_get_contents(recording.mbid, "rhythm", "aksharaPeriod", version=settings.FEAT_VERSION_RHYTHM)
        akshara = str(round(float(akshara), 3) * 1000)
    except docserver.exceptions.NoFileException:
        akshara = None

    try:
        pitchtrackurl = docserver.util.docserver_get_url(recording.mbid, "carnaticnormalisedpitch", "packedpitch", version=settings.FEAT_VERSION_CARNATIC_NORMALISED_PITCH)
        pitchtrackurl = request.build_absolute_uri(pitchtrackurl)
        histogramurl = docserver.util.docserver_get_url(recording.mbid, "carnaticnormalisedpitch", "drawhistogram", version=settings.FEAT_VERSION_CARNATIC_NORMALISED_PITCH)
        histogramurl = request.build_absolute_uri(histogramurl)
    except docserver.exceptions.NoFileException:
        pitchtrackurl = ""
        histogramurl = ""

    try:
        rhythmurl = docserver.util.docserver_get_url(recording.mbid, "rhythm", "aksharaTicks", version=settings.FEAT_VERSION_RHYTHM)
        rhythmurl = request.build_absolute_uri(rhythmurl)
        aksharaurl = docserver.util.docserver_get_url(recording.mbid, "rhythm", "APcurve", version=settings.FEAT_VERSION_RHYTHM)
        aksharaurl = request.build_absolute_uri(aksharaurl)
    except docserver.exceptions.NoFileException:
        rhythmurl = ""
        aksharaurl = ""

    try:
        permission = utils.get_user_permissions(request.user)
        concert = recording.concert_set.with_permissions(None, permission=permission).get()
        recordings = list(concert.recordings.all())
        recordingpos = recordings.index(recording)
    except Concert.DoesNotExist:
        concert = None
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
           "concert": concert,
           "bootleg": show_restricted,
           }

    return render(request, "carnatic/recording.html", ret)


@user_passes_test(dashboard.views.is_staff)
def formedit(request):
    concerts = Concert.objects.all().prefetch_related('artists')
    concerts = sorted(concerts, key=lambda c: sum([r.forms.count() for r in c.recordings.all().prefetch_related('forms')])*1.0/c.recordings.count())
    ret = {"concerts": concerts}
    return render(request, "carnatic/formedit.html", ret)


@user_passes_test(dashboard.views.is_staff)
def formconcert(request, uuid):
    concert = get_object_or_404(Concert, mbid=uuid)
    forms = Form.objects.all()

    dashrelease = dashboard.models.MusicbrainzRelease.objects.get(mbid=concert.mbid)

    if request.method == "POST":
        for i, t in enumerate(concert.tracklist()):
            fname = "form_%s" % i
            f = request.POST.get(fname)
            try:
                f = int(f)
                if len(t.forms.all()):
                    # If we already have a form, and it's different
                    # to the submitted one, remove
                    form = t.forms.get()
                    if f != form.id:
                        t.forms.clear()
                if len(t.forms.all()) == 0:
                    form = Form.objects.get(pk=f)
                    RecordingForm.objects.create(recording=t, form=form, sequence=1)

            except ValueError:
                # Not set, if we had one, remove it
                if len(t.forms.all()):
                    t.forms.clear()
                # Otherwise, do nothing

    tracks = []
    for i, t in enumerate(concert.tracklist()):
        tracks.append((i, t))
    ret = {"concert": concert, "tracks": tracks,
           "dashrelease": dashrelease, "forms": forms}
    return render(request, "carnatic/formconcert.html", ret)
