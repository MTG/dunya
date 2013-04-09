from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from carnatic.models import *
import json

def main(request):
    filter_items = [
            Artist.get_filter_criteria(),
            Concert.get_filter_criteria(),
            Work.get_filter_criteria(),
            Instrument.get_filter_criteria(),
            Raaga.get_filter_criteria(),
            Taala.get_filter_criteria()
        ]

    ret = {"filter_items": json.dumps(filter_items)
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

def artist(request, artistid):
    artist = get_object_or_404(Artist, pk=artistid)
    ret = {"artist": artist
          }

    return render(request, "carnatic/artist.html", ret)

def composer(request, composerid):
    composer = get_object_or_404(Composer, pk=composerid)
    ret = {"composer": composer}

    return render(request, "carnatic/composer.html", ret)

def concert(request, concertid):
    concert = get_object_or_404(Concert, pk=concertid)
    ret = {"concert": concert}

    return render(request, "carnatic/concert.html", ret)

def recording(request, recordingid):
    recording = get_object_or_404(Recording, pk=recordingid)

    ret = {"recording": recording}
    return render(request, "carnatic/recording.html", ret)

def work(request, workid):
    work = get_object_or_404(Work, pk=workid)

    ret = {"work": work}
    return render(request, "carnatic/work.html", ret)

def taala(request, taalaid):
    taala = get_object_or_404(Taala, pk=taalaid)

    ret = {"taala": taala}
    return render(request, "carnatic/taala.html", ret)

def raaga(request, raagaid):
    raaga = get_object_or_404(Raaga, pk=raagaid)

    ret = {"raaga": raaga}
    return render(request, "carnatic/raaga.html", ret)

def instrument(request, instrumentid):
    instrument = get_object_or_404(Instrument, pk=instrumentid)
    ret = {"instrument": instrument}

    return render(request, "carnatic/instrument.html", ret)
