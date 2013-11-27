# -*- coding: UTF-8 -*-
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q

import social.tagging as tagging
from carnatic.models import *
from carnatic import search
from social.forms import TagSaveForm
import json
import docserver
import collections
import math

def get_filter_items():
    filter_items = [
            Artist.get_filter_criteria(),
            Concert.get_filter_criteria(),
            Work.get_filter_criteria(),
            Instrument.get_filter_criteria(),
            Raaga.get_filter_criteria(),
            Taala.get_filter_criteria()
    ]
    return filter_items

def searchcomplete(request):
    term = request.GET.get("term")
    if term:
        suggestions = search.autocomplete(term)
        ret = [{"id": i, "label": l, "value": l} for i, l in enumerate(suggestions, 1)]
    else:
        ret = []
    return HttpResponse(json.dumps(ret), content_type="application/json")

def main(request):
    qartist = []
    if "a" in request.GET:
        for x in request.GET.getlist("a"):
            qartist.append(x)
    if "q" in request.GET:
        query = request.GET.get("q")
    else:
        query = None

    numartists = Artist.objects.count()
    numcomposers = Composer.objects.count()
    numraagas = Raaga.objects.count()
    numtaalas = Taala.objects.count()
    numconcerts = Concert.objects.count()
    numinstruments = Instrument.objects.count()
    numworks = Work.objects.count()

    if qartist:
        artists = []
        instruments = []
        concerts = []
        for aname in qartist:
            art = Artist.objects.get(name=aname)
            artists.append(art)
            instruments.append(art.instruments())
        concerts = Concert.objects.filter(artists__in=artists).all()
        results = True
    elif query:
        results = search.search(query)
        artists = results.get("artist", [])
        instruments = results.get("instrument", [])
        concerts = results.get("concert", [])
        raagas = results.get("raaga", [])
        taalas = results.get("taala", [])
        works = results.get("work", [])
        composers = results.get("composer", [])
        recordings = []

        numartists = len(artists)
        numcomposers = len(composers)
        numraagas = len(raagas)
        numtaalas = len(taalas)
        numconcerts = len(concerts)
        numinstruments = len(instruments)
        numworks = len(works)
        results = True
    else:
        print "something else"
        artists = Artist.objects.all()[:6]
        concerts = Concert.objects.all()[:6]
        instruments = Instrument.objects.all()[:6]
        results = None

        composers = Composer.objects.all()[:6]
        recordings = Recording.objects.all()[:6]
        raagas = Raaga.objects.all()[:6]
        taalas = Taala.objects.all()[:6][:6]
        works = Work.objects.all()[:6][:6]

    ret = {"numartists": numartists,
           "filter_items": json.dumps(get_filter_items()),
           "numcomposers": numcomposers,
           "numraagas": numraagas,
           "numtaalas": numtaalas,
           "numconcerts": numconcerts,
           "numworks": numworks,
           "numinstruments": numinstruments,

           "artists": artists,
           "composers": composers,
           "recordings": recordings,
           "concerts": concerts,
           "raagas": raagas,
           "taalas": taalas,
           "instruments": instruments,
           "works": works,
           "results": results,

           "query": query
           }

    return render(request, "carnatic/index.html", ret)

def artistsearch(request):
    artists = Artist.objects.all()
    ret = []
    for a in artists:
        ret.append({"mbid": a.mbid, "name": a.name})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def artist(request, artistid):
    artist = get_object_or_404(Artist, pk=artistid)

    inst = artist.instruments()
    ips = InstrumentPerformance.objects.filter(instrument=inst)
    similar_artists = []
    for i in ips:
        if i.performer not in similar_artists:
            similar_artists.append(i.performer)

    if artist.main_instrument and artist.main_instrument.percussion:
        taalamap = {}
        taalacount = collections.Counter()
        taalas = Taala.objects.filter(Q(work__recording__concert__artists=artist) | Q(work__recording__concert__instrumentconcertperformance__performer=artist) | Q(work__recording__instrumentperformance__performer=artist))
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
        raagas = Raaga.objects.filter(Q(work__recording__concert__artists=artist) | Q(work__recording__concert__instrumentconcertperformance__performer=artist) | Q(work__recording__instrumentperformance__performer=artist))
        for r in raagas:
            raagacount[r.name] += 1
            if r.name not in raagamap:
                raagamap[r.name] = r
        raagas = []
        for r, count in raagacount.most_common():
            raagas.append((raagamap[r], count))
    else:
        raagas = []

    tags = tagging.tag_cloud(artistid, "artist")
    musicbrainz = artist.get_musicbrainz_url()
    k = data.models.SourceName.objects.get(name="kutcheris.com")
    w = data.models.SourceName.objects.get(name="Wikipedia")
    kutcheris = None
    wikipedia = None
    kr = artist.references.filter(artist_source_set=k)
    if kr.count():
        kutcheris = kr[0].uri
    wr = artist.references.filter(artist_source_set=w)
    if wr.count():
        wikipedia = wr[0].uri
    desc = artist.description
    if desc and desc.source.source_name == k:
        kutcheris = artist.description.source.uri
    elif desc and desc.source.source_name == w:
        wikipedia = artist.description.source.uri

    ret = {"filter_items": json.dumps(get_filter_items()),
    	   "artist": artist,
           "form": TagSaveForm(),
            "objecttype": "artist",
            "objectid": artist.id,
            "tags": tags,
            "similar_artists": similar_artists,
            "raagas": raagas,
            "taalas": taalas,
            "mb": musicbrainz,
            "kutcheris": kutcheris,
            "wiki": wikipedia
    }

    return render(request, "carnatic/artist.html", ret)

def composer(request, composerid):
    composer = get_object_or_404(Composer, pk=composerid)
    ret = {"composer": composer, "filter_items": json.dumps(get_filter_items())}

    return render(request, "carnatic/composer.html", ret)

def concertsearch(request):
    concerts = Concert.objects.all()
    ret = []
    for c in concerts:
        ret.append({"mbid": c.mbid, "title": c.title})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def concert(request, concertid):
    concert = get_object_or_404(Concert, pk=concertid)
    images = concert.images.all()
    if images:
        image = images[0].image.url
    else:
        image = "/media/images/noconcert.jpg"

    samples = concert.tracks.all()[:2]

    tags = tagging.tag_cloud(concertid, "concert")

    # Other similar concerts
    similar = concert.get_similar()

    # Raaga in
    ret = {"filter_items": json.dumps(get_filter_items()),
           "concert": concert,
	   "form": TagSaveForm(),
	   "objecttype": "concert",
	   "objectid": concert.id,
	   "tags": tags,
       "image": image,
       "samples": samples,
       "similar_concerts": similar
       }

    return render(request, "carnatic/concert.html", ret)

def recording(request, recordingid):
    recording = get_object_or_404(Recording, pk=recordingid)

    tags = tagging.tag_cloud(recordingid, "recording")

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
        audio = docserver.util.docserver_get_url(recording.mbid, "mp3")
    except docserver.util.NoFileException:
        audio = None
    try:
        tonic = docserver.util.docserver_get_contents(recording.mbid, "ctonic", "tonic")
        notenames = ["A", "B♯", "B", "C", "C♯", "D", "E♯", "F", "F♯", "G", "A♯"]
        tonic = round(float(tonic), 2)
        thebin = (12 * math.log(tonic/440.0) / math.log(2)) % 12
        thebin = int(math.ceil(thebin))
        tonic = str(tonic) 
        if thebin < 10 and thebin >= 0:
            tonicname = notenames[thebin]
        else:
            print "bin is", thebin, "weird"
            print tonic
            print (12 * math.log(tonic/440.0) / math.log(2))
    except docserver.util.NoFileException:
        tonic = None
        tonicname = None
    try:
        akshara = docserver.util.docserver_get_contents(recording.mbid, "rhythm", "aksharaPeriod")
        akshara = str(round(float(akshara), 3) * 1000)
    except docserver.util.NoFileException:
        akshara = None

    try:
        pitchtrackurl = docserver.util.docserver_get_url(recording.mbid, "normalisedpitch", "packedpitch")
        histogramurl = docserver.util.docserver_get_url(recording.mbid, "normalisedpitch", "drawhistogram")
        rhythmurl = docserver.util.docserver_get_url(recording.mbid, "rhythm", "aksharaTicks")
        aksharaurl = docserver.util.docserver_get_url(recording.mbid, "rhythm", "APcurve")
    except docserver.util.NoFileException:
        pitchtrackurl = None
        histogramurl = None
        rhythmurl = None
        aksharaurl = None

    concert = recording.concert_set.get()
    tracks = list(concert.tracks.all())
    recordingpos = tracks.index(recording)
    nextrecording = None
    prevrecording = None
    if recordingpos > 0:
        prevrecording = tracks[recordingpos-1]
    if recordingpos+1 < len(tracks):
        nextrecording = tracks[recordingpos+1]
    mbid = recording.mbid

    ret = {"filter_items": json.dumps(get_filter_items()),
    	   "recording": recording,
           "form": TagSaveForm(),
            "objecttype": "recording",
            "objectid": recording.id,
            "tags": tags,
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
            "aksharaurl": aksharaurl
    }

    return render(request, "carnatic/recording.html", ret)

def worksearch(request):
    works = Work.objects.all()
    ret = []
    for w in works:
        ret.append({"mbid": w.mbid, "title": w.title})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def work(request, workid):
    work = get_object_or_404(Work, pk=workid)

    tags = tagging.tag_cloud(workid, "work")

    ret = {"filter_items": json.dumps(get_filter_items()),
           "work": work,
           "form": TagSaveForm(),
            "objecttype": "work",
            "objectid": work.id,
            "tags": tags,
    }
    return render(request, "carnatic/work.html", ret)

def taalasearch(request):
    taalas = Taala.objects.all()
    ret = []
    for t in taalas:
        ret.append({"pk": t.pk, "name": t.name})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def taala(request, taalaid):
    taala = get_object_or_404(Taala, pk=taalaid)

    similar = taala.get_similar()

    ret = {"taala": taala, "filter_items": json.dumps(get_filter_items()), "similar": similar}
    return render(request, "carnatic/taala.html", ret)

def raagasearch(request):
    raagas = Raaga.objects.all()
    ret = []
    for r in raagas:
        ret.append({"pk": r.pk, "name": r.name})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def raaga(request, raagaid):
    raaga = get_object_or_404(Raaga, pk=raagaid)
    similar = raaga.get_similar()

    ret = {"raaga": raaga, "filter_items": json.dumps(get_filter_items()), "similar": similar}
    return render(request, "carnatic/raaga.html", ret)

def instrumentsearch(request):
    instruments = Instrument.objects.all()
    ret = []
    for i in instruments:
        ret.append({"pk": i.pk, "name": i.name})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def instrument(request, instrumentid):
    instrument = get_object_or_404(Instrument, pk=instrumentid)
    ret = {"instrument": instrument, "filter_items": json.dumps(get_filter_items())}

    return render(request, "carnatic/instrument.html", ret)
