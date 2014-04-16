from django.shortcuts import render, get_object_or_404, redirect

import carnatic
from motifdiscovery import models
from sendfile import sendfile
import os

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

def servesegment(request, segmentid):
    seg = get_object_or_404(models.Segment, pk=segmentid)
    fname = os.path.join("/serve", seg.segment_path)
    response = sendfile(request, fname, mimetype="audio/mpeg")
    return response
