import json
import os

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django_sendfile import sendfile

import carnatic.models
from motifdiscovery import models


def main(request):
    return render(request, "motifdiscovery/index.html")


def artists(request):
    f = models.File.objects.using("motif").filter(hasseed=1)
    mbids = [m.mbid for m in f]
    arts = (
        carnatic.models.Artist.objects.filter(primary_concerts__recordings__mbid__in=mbids).distinct().order_by("name")
    )
    ret = {"artists": arts}
    return render(request, "motifdiscovery/artists.html", ret)


def artist(request, uuid):
    a = get_object_or_404(carnatic.models.Artist, mbid=uuid)
    f = models.File.objects.using("motif").filter(hasseed=1)
    mbids = [m.mbid for m in f]
    concerts = a.primary_concerts.filter(recordings__mbid__in=mbids).distinct()
    ret = {"artist": a, "concerts": concerts}
    return render(request, "motifdiscovery/artist.html", ret)


def release(request, uuid):
    r = get_object_or_404(carnatic.models.Concert, mbid=uuid)
    f = models.File.objects.using("motif").filter(hasseed=1)
    mbids = [m.mbid for m in f]
    tracks = r.recordings.filter(mbid__in=mbids)

    ret = {"release": r, "tracks": tracks}
    return render(request, "motifdiscovery/release.html", ret)


def seeds(request, uuid):
    """Seed pattern matches always occur in the same file. This means that Match.source.file
    and Match.target.file are always the same, therefore when we get matches we only check source"""
    rec = get_object_or_404(carnatic.models.Recording, mbid=uuid)
    matches = (
        models.Match.objects.using("motif")
        .filter(source__file__mbid=uuid)
        .filter(version=-1)
        .order_by("distance")
        .prefetch_related("source__segment")
        .prefetch_related("source__file")
        .prefetch_related("target__file")
        .prefetch_related("target__segment")
    )

    ret = {"recording": rec, "matches": matches}
    return render(request, "motifdiscovery/seeds.html", ret)


def results(request, uuid, seedid):
    rec = get_object_or_404(carnatic.models.Recording, mbid=uuid)
    matches = (
        models.Match.objects.using("motif")
        .filter(source=seedid, version=1)
        .order_by("distance")
        .prefetch_related("source")
        .prefetch_related("target")
        .prefetch_related("target__file")
        .prefetch_related("target__segment")
    )
    ret = {"recording": rec, "matches": matches}
    return render(request, "motifdiscovery/results.html", ret)


def similar(request):
    return render(request, "motifdiscovery/similar.html")


def servesegment(request, segmentid):
    seg = get_object_or_404(models.Segment, pk=segmentid)
    fname = os.path.join("/serve", seg.segment_path)
    response = sendfile(request, fname, mimetype="audio/mpeg")
    return response


def recinformation(request, uuid):
    ret = []
    matches = (
        models.Match.objects.using("motif")
        .filter(source__file__mbid=uuid)
        .filter(version=-1)
        .filter(distance__lt=1150000)
        .order_by("distance")
        .prefetch_related("source__segment")
        .prefetch_related("source__file")
        .prefetch_related("target__file")
        .prefetch_related("target__segment")
    )

    for m in matches[:100]:
        matches = (
            models.Match.objects.using("motif")
            .filter(source=m.source, version=1, distance__lt=4000)
            .order_by("distance")
            .prefetch_related("source")
            .prefetch_related("target")
            .prefetch_related("target__file")
            .prefetch_related("target__segment")
        )

        matches_local = matches.filter(target__file__mbid=uuid)[:100]
        matches_other = matches.exclude(target__file__mbid=uuid)[:100]
        ret.append(
            (
                (m.source.start_time, m.source.end_time),
                [(l.target.start_time, l.target.end_time) for l in matches_local],
                [(l.target.file.mbid, l.target.start_time, l.target.end_time) for l in matches_other],
            )
        )

    return HttpResponse(json.dumps(ret), content_type="application/json")
