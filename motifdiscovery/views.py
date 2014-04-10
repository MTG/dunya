from django.shortcuts import render, get_object_or_404, redirect

import carnatic
from motifdiscovery import models

def main(request):
    return render(request, "motifdiscovery/index.html")

def artists(request):
    arts = carnatic.models.Artist.objects.all()
    ret = {"artists": arts}
    return render(request, "motifdiscovery/artists.html", ret)

def artist(request, uuid):
    a = get_object_or_404(carnatic.models.Artist, mbid=uuid)
    ret = {"artist": a}
    return render(request, "motifdiscovery/artist.html", ret)

def release(request, uuid):
    r = get_object_or_404(carnatic.models.Concert, mbid=uuid)
    ret = {"release": r}
    return render(request, "motifdiscovery/release.html", ret)

def seeds(request, uuid):
    rec = get_object_or_404(carnatic.models.Recording, mbid=uuid)
    patterns = models.Pattern.objects.using('motif').filter(file__mbid=uuid, isseed=1)
    ret = {"recording": rec, "patterns": patterns}
    return render(request, "motifdiscovery/seeds.html", ret)

def results(request, seedpair):
    pass
