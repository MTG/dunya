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

from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.conf import settings
from django.templatetags.static import static

from data import utils
from carnatic.models import *
from carnatic import search
import json
import docserver
import dashboard.views
import collections
import math
import random
import pysolr

def get_filter_items():
    filter_items = [
        Artist.get_filter_criteria(),
        Concert.get_filter_criteria(),
        Instrument.get_filter_criteria(),
        Raaga.get_filter_criteria(),
        Taala.get_filter_criteria()
    ]
    return filter_items

def searchcomplete(request):
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
    qraaga = []
    qtaala = []
    qconcert = []
    if len(request.GET) == 0:
        # We have a 'default' query. If there's no other query we pre-seed it
        # G. N. Balasubramaniam
        qartist = [10]
        # thodi raaga
        qraaga = [55]
        return redirect("%s?a=10&r=55" % reverse('carnatic-main'))
    if "a" in request.GET:
        for i in request.GET.getlist("a"):
            qartist.append(int(i))
    if "i" in request.GET:
        for i in request.GET.getlist("i"):
            qinstr.append(int(i))
    if "c" in request.GET:
        for i in request.GET.getlist("c"):
            qconcert.append(int(i))
    if "r" in request.GET:
        for i in request.GET.getlist("r"):
            qraaga.append(int(i))
    if "t" in request.GET:
        for i in request.GET.getlist("t"):
            qtaala.append(int(i))
    if "q" in request.GET:
        query = request.GET.get("q")
    else:
        query = None

    numartists = Artist.objects.filter(dummy=False).count()
    numcomposers = Composer.objects.count()
    numraagas = Raaga.objects.count()
    numtaalas = Taala.objects.count()
    numconcerts = Concert.objects.count()
    numinstruments = Instrument.objects.count()
    numworks = Work.objects.count()

    displayres = []
    querybrowse = False
    searcherror = False

    show_bootlegs = request.show_bootlegs

    if qartist:
        # TODO: If instrument set, only show artists who perform this instrument
        querybrowse = True

        # If raaga or taala is set, make a list to filter concerts by
        rlist = []
        tlist = []
        if qraaga:
            for rid in qraaga:
                ra = Raaga.objects.get(pk=rid)
                rlist.append(ra)
        if qtaala:
            for tid in qtaala:
                ta = Taala.objects.get(pk=tid)
                tlist.append(ta)

        if len(qartist) == 1:
            # If there is one artist selected, show their concerts
            # (optionally filtered by raaga or taala)
            aid = qartist[0]
            art = Artist.objects.get(pk=aid)
            displayres.append(("artist", art))
            if art.main_instrument:
                displayres.append(("instrument", art.main_instrument))
            for ra in rlist:
                displayres.append(("raaga", ra))
            for ta in tlist:
                displayres.append(("taala", ta))
            for c in art.concerts(raagas=rlist, taalas=tlist, with_bootlegs=show_bootlegs):
                displayres.append(("concert", c))
        else:
            # Otherwise if more than one artist is selected,
            # show only concerts that all artists perform in
            allconcerts = []
            for aid in qartist:
                art = Artist.objects.get(pk=aid)
                displayres.append(("artist", art))
                if art.main_instrument:
                    displayres.append(("instrument", art.main_instrument))
                thisconcerts = set(art.concerts(raagas=rlist, taalas=tlist, with_bootlegs=show_bootlegs))
                allconcerts.append(thisconcerts)
            combinedconcerts = reduce(lambda x, y: x & y, allconcerts)

            for ra in rlist:
                displayres.append(("raaga", ra))
            for ta in tlist:
                displayres.append(("taala", ta))

            for c in list(combinedconcerts):
                displayres.append(("concert", c))

    elif qinstr:  # instrument query, but no artist
        querybrowse = True
        # instrument, people
        for iid in qinstr:
            instr = Instrument.objects.get(pk=iid)
            displayres.append(("instrument", instr))
            for p in instr.ordered_performers()[:5]:
                displayres.append(("artist", p))

    elif qraaga:
        querybrowse = True
        # raaga, people
        for rid in qraaga:
            ra = Raaga.objects.get(pk=rid)
            displayres.append(("raaga", ra))
            artists = ra.artists()
            if qinstr:
                # if instrument, only people who play that
                artists = artists.filter(main_instrument__in=qinstr)
            for a in artists[:5]:
                displayres.append(("artist", a))
    elif qtaala:
        querybrowse = True
        # taala, people
        for tid in qtaala[:5]:
            ta = Taala.objects.get(pk=tid)
            displayres.append(("taala", ta))
            percussionists = ta.percussion_artists()
            for a in ta.artists():
                if a not in percussionists:
                    percussionists.append(a)
            # TODO: We could order by percussionists, or by number of times they've
            # performed this taala, or by people with images
            artists = percussionists[:5]
            if qinstr:
                # if instrument, only people who play that
                artists = artists.filter(main_instrument__in=qinstr)
            for a in artists:
                displayres.append(("artist", a))
    elif qconcert:
        querybrowse = True
        # concert, people
        for cid in qconcert:
            try:
                permission = utils.get_user_permissions(request.user)
                con = Concert.objects.with_permissions(permission).get(pk=cid)
                displayres.append(("concert", con))
                artists = con.performers()
                for a in artists:
                    displayres.append(("artist", a))
                    # if instrument, only people who play that?
            except Concert.DoesNotExist:
                pass
    elif query:
        try:
            results = search.search(query, with_bootlegs=show_bootlegs)
        except pysolr.SolrError:
            searcherror = True
            results = {}
        artists = results.get("artist", [])
        instruments = results.get("instrument", [])
        concerts = results.get("concert", [])
        raagas = results.get("raaga", [])
        taalas = results.get("taala", [])

        displayres = []
        for a in artists:
            displayres.append(("artist", a))
        for i in instruments:
            displayres.append(("instrument", i))
        for c in concerts:
            displayres.append(("concert", c))
        for r in raagas:
            displayres.append(("raaga", r))
        for t in taalas:
            displayres.append(("taala", t))

        numartists = len(artists)
        numraagas = len(raagas)
        numtaalas = len(taalas)
        numconcerts = len(concerts)
        numinstruments = len(instruments)
        results = True
    else:
        results = None

        displayres = []

    if displayres:
        numartists = len([i for i in displayres if i[0] == "artist"])
        numraagas = len([i for i in displayres if i[0] == "raaga"])
        numtaalas = len([i for i in displayres if i[0] == "taala"])
        numconcerts = len([i for i in displayres if i[0] == "concert"])
        numinstruments = len([i for i in displayres if i[0] == "instrument"])

    ret = {"numartists": numartists,
           "filter_items": json.dumps(get_filter_items()),
           "numcomposers": numcomposers,
           "numraagas": numraagas,
           "numtaalas": numtaalas,
           "numconcerts": numconcerts,
           "numworks": numworks,
           "numinstruments": numinstruments,

           "results": displayres,

           "querytext": query,
           "querybrowse": querybrowse,
           "qartist": json.dumps(qartist),
           "qinstr": json.dumps(qinstr),
           "qraaga": json.dumps(qraaga),
           "qtaala": json.dumps(qtaala),
           "qconcert": json.dumps(qconcert),
           "searcherror": searcherror
           }

    return render(request, "carnatic/index.html", ret)

def artistsearch(request):
    artists = Artist.objects.filter(dummy=False).order_by('name')
    ret = []
    for a in artists:
        ret.append({"id": a.id, "name": a.name})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def artistbyid(request, artistid, name=None):
    artist = get_object_or_404(Artist, pk=artistid)
    return redirect(artist.get_absolute_url(), permanent=True)

def artist(request, uuid, name=None):
    artist = get_object_or_404(Artist, mbid=uuid)

    inst = artist.instruments()
    ips = InstrumentPerformance.objects.filter(instrument=inst)
    similar_artists = []
    for i in ips:
        if i.artist not in similar_artists:
            similar_artists.append(i.artist)

    if artist.main_instrument and artist.main_instrument.percussion:
        taalamap = {}
        taalacount = collections.Counter()
        taalas = Taala.objects.filter(Q(work__recording__concert__artists=artist) | Q(work__recording__instrumentperformance__artist=artist))
        for t in taalas:
            taalacount[t.name] += 1
            if t.name not in taalamap:
                taalamap[t.name] = t
        taalas = []
        for t, count in taalacount.most_common():
            taalas.append((taalamap[t], count))
    else:
        taalas = []
    # vocalist or violinist
    if artist.main_instrument and artist.main_instrument.id in [1, 2]:
        raagamap = {}
        raagacount = collections.Counter()
        raagas = Raaga.objects.filter(Q(work__recording__concert__artists=artist) | Q(work__recording__instrumentperformance__artist=artist))
        for r in raagas:
            raagacount[r.name] += 1
            if r.name not in raagamap:
                raagamap[r.name] = r
        raagas = []
        for r, count in raagacount.most_common():
            raagas.append((raagamap[r], count))
    else:
        raagas = []

    musicbrainz = artist.get_musicbrainz_url()
    k = data.models.SourceName.objects.get(name="kutcheris.com")
    w = data.models.SourceName.objects.get(name="Wikipedia")
    kutcheris = None
    wikipedia = None
    desc = artist.description
    if desc and desc.source.source_name == k:
        kutcheris = artist.description.source.uri
    elif desc and desc.source.source_name == w:
        wikipedia = artist.description.source.uri
    kr = artist.references.filter(source_name=k)
    if kr.count() and not kutcheris:
        kutcheris = kr[0].uri
    wr = artist.references.filter(source_name=w)
    if wr.count() and not wikipedia:
        wikipedia = wr[0].uri

    # Sample is the first recording of any of their concerts (Vignesh, Dec 9)
    concerts = artist.concerts()
    sample = None
    if concerts:
        recordings = concerts[0].recordings.all()
        if recordings:
            sample = recordings[0]

    ret = {"filter_items": json.dumps(get_filter_items()),
           "artist": artist,
           "objecttype": "artist",
           "objectid": artist.id,
           "similar_artists": similar_artists,
           "raagas": raagas,
           "taalas": taalas,
           "sample": sample,
           "mb": musicbrainz,
           "kutcheris": kutcheris,
           "wiki": wikipedia
           }

    return render(request, "carnatic/artist.html", ret)

def composerbyid(request, composerid, name=None):
    composer = get_object_or_404(Composer, pk=composerid)
    return redirect(composer.get_absolute_url(), permanent=True)

def composer(request, uuid, name=None):
    composer = get_object_or_404(Composer, mbid=uuid)

    works = composer.works.all()
    # We show all compositions, ordered by number of recordings
    works = sorted(works, key=lambda w: w.recording_set.count(), reverse=True)

    musicbrainz = composer.get_musicbrainz_url()
    w = data.models.SourceName.objects.get(name="Wikipedia")
    wikipedia = None
    wr = composer.references.filter(source_name=w)
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

    return render(request, "carnatic/composer.html", ret)

def concertsearch(request):
    permissions = utils.get_user_permissions(request.user)
    concerts = Concert.objects.with_permissions(permissions).order_by('title')
    #concerts = Concert.objects.with_bootlegs(request.show_bootlegs).order_by('title')
    ret = []
    for c in concerts:
        title = "%s<br>%s" % (c.title, c.artistcredit)
        if c.bootleg:
            title = '<img src="%s" title="bootleg concert" /> %s' % (static('carnatic/img/cassette.png'), title)
        ret.append({"id": c.id, "title": title})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def concertbyid(request, concertid, title=None):
    concert = get_object_or_404(Concert, pk=concertid)
    return redirect(concert.get_absolute_url(), permanent=True)

def concert(request, uuid, title=None):
    concert = get_object_or_404(Concert, mbid=uuid)

    bootleg = False
    if concert.bootleg and request.show_bootlegs:
        bootleg = True
    elif concert.bootleg and not request.show_bootlegs:
        raise Http404

    images = concert.images.all()
    if images:
        image = images[0].image.url
    else:
        image = "/media/images/noconcert.jpg"
    sample = None
    recordings = concert.recordings.all()
    if recordings:
        sample = recordings[:1]

    # Other similar concerts
    similar = concert.get_similar()

    # Raaga in
    ret = {"filter_items": json.dumps(get_filter_items()),
           "concert": concert,
           "objecttype": "concert",
           "objectid": concert.id,
           "image": image,
           "sample": sample,
           "similar_concerts": similar,
           "recordings": recordings,
           "bootleg": bootleg
           }

    return render(request, "carnatic/concert.html", ret)

def recordingbyid(request, recordingid, title=None):
    recording = get_object_or_404(Recording, pk=recordingid)
    return redirect(recording.get_absolute_url(), permanent=True)

def recording(request, uuid, title=None):
    recording = get_object_or_404(Recording, mbid=uuid)

    bootleg = False
    if recording.is_bootleg() and request.show_bootlegs:
        bootleg = True
    elif recording.is_bootleg() and not request.show_bootlegs:
        raise Http404

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
    try:
        akshara = docserver.util.docserver_get_contents(recording.mbid, "rhythm", "aksharaPeriod", version=settings.FEAT_VERSION_RHYTHM)
        akshara = str(round(float(akshara), 3) * 1000)
    except docserver.util.NoFileException:
        akshara = None

    try:
        pitchtrackurl = docserver.util.docserver_get_url(recording.mbid, "normalisedpitch", "packedpitch", version=settings.FEAT_VERSION_NORMALISED_PITCH)
        histogramurl = docserver.util.docserver_get_url(recording.mbid, "normalisedpitch", "drawhistogram", version=settings.FEAT_VERSION_NORMALISED_PITCH)
        rhythmurl = docserver.util.docserver_get_url(recording.mbid, "rhythm", "aksharaTicks", version=settings.FEAT_VERSION_RHYTHM)
        aksharaurl = docserver.util.docserver_get_url(recording.mbid, "rhythm", "APcurve", version=settings.FEAT_VERSION_RHYTHM)
    except docserver.util.NoFileException:
        pitchtrackurl = "/document/by-id/%s/%s?subtype=%s&v=%s" % (recording.mbid, "normalisedpitch", "packedpitch", settings.FEAT_VERSION_NORMALISED_PITCH)
        histogramurl = "/document/by-id/%s/%s?subtype=%s&v=%s" % (recording.mbid, "normalisedpitch", "drawhistogram", settings.FEAT_VERSION_NORMALISED_PITCH)
        rhythmurl = "/document/by-id/%s/%s?subtype=%s&v=%s" % (recording.mbid, "rhythm", "aksharaTicks", settings.FEAT_VERSION_RHYTHM)
        aksharaurl = "/document/by-id/%s/%s?subtype=%s&v=%s" % (recording.mbid, "rhythm", "APcurve", settings.FEAT_VERSION_RHYTHM)

    similar = []
    try:
        similar_mbids = search.similar_recordings(recording.mbid)
        for m in similar_mbids:
            try:
                rec = Recording.objects.get(mbid=m[0])
                similar.append(rec)
            except Recording.DoesNotExist:
                pass
    except pysolr.SolrError:
        # TODO: Show error in similar recordings page instead of empty
        pass
    similar = similar[:10]

    try:
        concert = recording.concert_set.get()
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

    ret = {"filter_items": json.dumps(get_filter_items()),
           "recording": recording,
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
           "similar": similar,
           "concert": concert,
           "bootleg": bootleg,
           }

    return render(request, "carnatic/recording.html", ret)

def worksearch(request):
    works = Work.objects.all()
    ret = []
    for w in works:
        ret.append({"id": w.id, "title": w.title})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def workbyid(request, workid, title=None):
    work = get_object_or_404(Work, pk=workid)
    return redirect(work.get_absolute_url(), permanent=True)

def work(request, uuid, title=None):
    work = get_object_or_404(Work, mbid=uuid)

    recordings = work.recording_set.all()
    if len(recordings):
        sample = random.sample(recordings, 1)
    else:
        sample = None

    ret = {"filter_items": json.dumps(get_filter_items()),
           "work": work,
           "objecttype": "work",
           "objectid": work.id,
           "sample": sample,
           }
    return render(request, "carnatic/work.html", ret)

def taalasearch(request):
    taalas = Taala.objects.all().order_by('name')
    ret = []
    for t in taalas:
        ret.append({"id": t.id, "name": str(t)})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def taalabyid(request, taalaid, name=None):
    taala = get_object_or_404(Taala, pk=taalaid)
    return redirect(taala.get_absolute_url(), permanent=True)

def taala(request, uuid, name=None):
    taala = get_object_or_404(Taala, uuid=uuid)

    similar = taala.get_similar()
    recordings = taala.recordings(10)
    sample = None
    if len(recordings):
        sample = random.sample(recordings, 1)[0]

    ret = {"taala": taala,
           "sample": sample,
           "similar": similar
           }
    return render(request, "carnatic/taala.html", ret)

def raagasearch(request):
    raagas = Raaga.objects.all().order_by('name')
    ret = []
    for r in raagas:
        ret.append({"id": r.id, "name": str(r)})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def raagabyid(request, raagaid, name=None):
    raaga = get_object_or_404(Raaga, pk=raagaid)
    return redirect(raaga.get_absolute_url(), permanent=True)

def raaga(request, uuid, name=None):
    raaga = get_object_or_404(Raaga, uuid=uuid)
    similar = raaga.get_similar()
    recordings = raaga.recordings(10)
    sample = None
    if len(recordings):
        sample = random.sample(recordings, 1)[0]

    ret = {"raaga": raaga,
           "sample": sample,
           "similar": similar
           }
    return render(request, "carnatic/raaga.html", ret)

def instrumentsearch(request):
    instruments = Instrument.objects.all().order_by('name')
    ret = []
    for i in instruments:
        ret.append({"id": i.id, "name": i.name})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def instrumentbyid(request, instrumentid, name=None):
    instrument = get_object_or_404(Instrument, pk=instrumentid)
    return redirect(instrument.get_absolute_url(), permanent=True)

def instrument(request, uuid, name=None):
    instrument = get_object_or_404(Instrument, mbid=uuid)
    samples = instrument.samples(10)
    sample = None
    if samples:
        sample = samples[0]
    ret = {"instrument": instrument,
           "sample": sample,
           "filter_items": json.dumps(get_filter_items())
           }

    return render(request, "carnatic/instrument.html", ret)

@user_passes_test(dashboard.views.is_staff)
def formedit(request):
    concerts = Concert.objects.all()
    ret = {"concerts": concerts}
    return render(request, "carnatic/formedit.html", ret)

from django import forms
from django.forms.models import modelform_factory

@user_passes_test(dashboard.views.is_staff)
def formconcert(request, uuid):
    concert = get_object_or_404(Concert, mbid=uuid)
    WorkForm = modelform_factory(Work, fields=('form', ))

    dashrelease = dashboard.models.MusicbrainzRelease.objects.get(mbid=concert.mbid)

    if request.method == "POST":
        for i, t in enumerate(concert.tracklist()):
            w = t.work
            form = WorkForm(request.POST, instance=w, prefix="tr%s" % i)
            if form.is_valid():
                form.save()


    tracks = []
    for i, t in enumerate(concert.tracklist()):
        w = t.work
        form = WorkForm(instance=w, prefix="tr%s" % i)
        tracks.append((t, w, form))
    ret = {"concert": concert, "tracks": tracks, "dashrelease": dashrelease}
    return render(request, "carnatic/formconcert.html", ret)
