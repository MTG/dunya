from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from data.models import *

def main(request):
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
    return render(request, "carnatic/index.html", ret)

def artist(request, artistid):
    artist = get_object_or_404(Artist, pk=artistid)
    ret = {"artist": artist
          }

    return render(request, "carnatic/artist.html", ret)

def composer(request, composerid):
    composer = get_object_or_404(Composer, pk=composerid)

    return render(request, "carnatic/composer.html")

def concert(request, concertid):
    concert = get_object_or_404(Concert, pk=concertid)
    ret = {"concert": concert}

    return render(request, "carnatic/concert.html", ret)

def recording(request, recordingid):
    recording = get_object_or_404(Recording, pk=recordingid)

    return render(request, "carnatic/recording.html")

def taala(request, taalaid):
    taala = get_object_or_404(Taala, pk=taalaid)

    return render(request, "carnatic/taala.html")

def raaga(request, raagaid):
    raaga = get_object_or_404(Raaga, pk=raagaid)

    return render(request, "carnatic/raaga.html")

def instrument(request, instrumentid):
    instrument = get_object_or_404(Instrument, pk=instrumentid)

    return render(request, "carnatic/instrument.html")
