from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
import social.tagging as tagging

from carnatic.models import *
from social.forms import TagSaveForm
import json

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

def main(request):
    qartist = []
    if "a" in request.GET:
        for x in request.GET.getlist("a"):
            qartist.append(x)
    artistquery = request.GET.get('a');
    numartists = Artist.objects.count()
    numcomposers = Composer.objects.count()
    numrecordings = Recording.objects.count()
    numraaga = Raaga.objects.count()
    numtaala = Taala.objects.count()
    numconcert = Concert.objects.count()

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

    ret = {"numartists": numartists,
           "filter_items": json.dumps(get_filter_items()),
           "numcomposers": numcomposers,
           "numrecordings": numrecordings,
           "numraaga": numraaga,
           "numtaala": numtaala,
           "numconcert": numconcert,

           "artists": artists,
           "composers": composers,
           "recordings": recordings,
           "concerts": concerts,
           "raagas": raagas,
           "taalas": taalas,
           "instruments": instruments,
           "results": results,
           }
    return render(request, "carnatic/index.html", ret)

def overview(request):
    numartists = Artist.objects.count()
    artists = Artist.objects.all()
    numcomposers = Composer.objects.count()
    composers = Composer.objects.all()
    numrecordings = Recording.objects.count()
    recordings = Recording.objects.all()
    concerts = Concert.objects.all()
    raagas = Raaga.objects.all()
    taalas = Taala.objects.all()
    instruments = Instrument.objects.all()
    numraaga = Raaga.objects.count()
    numtaala = Taala.objects.count()

    ret = {"numartists": numartists,
           "numcomposers": numcomposers,
           "numrecordings": numrecordings,
           "numraaga": numraaga,
           "numtaala": numtaala,

           "artists": artists,
           "composers": composers,
           "recordings": recordings,
           "concerts": concerts,
           "raagas": raagas,
           "taalas": taalas,
           "instruments": instruments
           }
    return render(request, "carnatic/overview.html", ret)

def artistsearch(request):
    artists = Artist.objects.all()
    ret = []
    for a in artists:
        ret.append({"mbid": a.mbid, "name": a.name})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def get_image(entity, noimage):
    images = entity.images.all()
    if images:
        image = images[0].image.url
    else:
        image = "/media/images/%s.jpg" % noimage
    return image

def artist(request, artistid):
    artist = get_object_or_404(Artist, pk=artistid)

    inst = artist.instruments()
    ips = InstrumentPerformance.objects.filter(instrument=inst)
    similar_artists = []
    for i in ips:
        if i.performer not in similar_artists:
            similar_artists.append(i.performer)

    tags = tagging.tag_cloud(artistid, "artist")
    
    ret = {"filter_items": json.dumps(get_filter_items()),
    	   "artist": artist,
           "image": get_image(artist, "noartist"),
           "form": TagSaveForm(),
            "objecttype": "artist",
            "objectid": artist.id,
            "tags": tags,
            "similar_artists": similar_artists
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
    
    # Other concerts by the same person
    # XXX: Sort by if there's an image
    artist_concerts = Concert.objects.filter(artists__in=concert.artists.all()).all().distinct()
    works = [t.work for t in concert.tracks.all()]
    work_concerts = Concert.objects.filter(tracks__work__in=works).all().distinct()
    raagas = []
    taalas = []
    for t in concert.tracks.all():
        if t.work:
            raagas.extend(t.work.raaga.all())
            taalas.extend(t.work.taala.all())
    raaga_concerts = Concert.objects.filter(tracks__work__raaga__in=raagas).all().distinct()
    taala_concerts = Concert.objects.filter(tracks__work__taala__in=taalas).all().distinct()
    work_concerts = sorted(work_concerts, key=lambda c: len(c.images.all()), reverse=True)
    raaga_concerts = sorted(raaga_concerts, key=lambda c: len(c.images.all()), reverse=True)
    taala_concerts = sorted(taala_concerts, key=lambda c: len(c.images.all()), reverse=True)
    artist_concerts = sorted(artist_concerts, key=lambda c: len(c.images.all()), reverse=True)


    # Raaga in
    ret = {"filter_items": json.dumps(get_filter_items()),
           "concert": concert,
	   "artist_concerts": artist_concerts,
	   "work_concerts": work_concerts,
	   "raaga_concerts": raaga_concerts,
	   "taala_concerts": taala_concerts,
	   "form": TagSaveForm(),
	   "objecttype": "concert",
	   "objectid": concert.id,
	   "tags": tags,
       "image": image,
       "samples": samples
       }

    return render(request, "carnatic/concert.html", ret)

def recording(request, recordingid):
    recording = get_object_or_404(Recording, pk=recordingid)
    
    tags = tagging.tag_cloud(recordingid, "recording")
    
    ret = {"filter_items": json.dumps(get_filter_items()),
    	   "recording": recording,
           "form": TagSaveForm(),
            "objecttype": "recording",
            "objectid": recording.id,
            "tags": tags,
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

    ret = {"taala": taala, "filter_items": json.dumps(get_filter_items())}
    return render(request, "carnatic/taala.html", ret)

def raagasearch(request):
    raagas = Raaga.objects.all()
    ret = []
    for r in raagas:
        ret.append({"pk": r.pk, "name": r.name})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def raaga(request, raagaid):
    raaga = get_object_or_404(Raaga, pk=raagaid)

    ret = {"raaga": raaga, "filter_items": json.dumps(get_filter_items())}
    return render(request, "carnatic/raaga.html", ret)

def instrumentsearch(request):
    instruments = Instrument.objects.all()
    ret = []
    for i in instruments:
        ret.append({"pk": i.pk, "name": i.name})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def instrument(request, instrumentid):
    instrument = get_object_or_404(Instrument, pk=instrumentid)
    ret = {"instrument": instrument, "filter_items": json.dumps(get_filter_items()),
           "image": get_image(instrument, "noinstrument")}

    return render(request, "carnatic/instrument.html", ret)
