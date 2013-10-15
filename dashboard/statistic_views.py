from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count

from dashboard import models
from dashboard import views
import docserver
import carnatic

import json
import compmusic

def _common_stats(collectionid):
    releases = models.MusicbrainzRelease.objects.filter(collection__id=collectionid)
    ret = {}
    if releases.count():
        total_releases = releases.count()
        releases_ignored = releases.filter(ignore=True).count()
        counts = releases.annotate(Count('collectiondirectory'))
        releases_missing_dir = len([r for r in counts if r.collectiondirectory__count==0])
        ret["releases"] = total_releases
        ret["releases_ignored"] = releases_ignored
        ret["releases_missing"] = releases_missing_dir

        num_recordings = models.CollectionFile.objects.filter(
                directory__musicbrainzrelease__collection__id=collectionid).count()
        ret["recordings"] = num_recordings
    else:
        ret["missing"] = True
    return ret

def _raaga_taala_by_results(collectionid):
    ret = {}
    raagachecker = "dashboard.completeness.RaagaTaalaFile"
    raagas = set()
    taalas = set()
    results = models.CollectionFileResult.objects.filter(
           collectionfile__directory__musicbrainzrelease__collection__id=collectionid).filter(
           checker__module=raagachecker)
    for r in results.all():
        data = json.loads(r.data) if r.data else {}
        thistaala = data.get("taala", [])
        thisraaga = data.get("raaga", [])
        [raagas.add(tr) for tr in thisraaga]
        [taalas.add(tt) for tt in thistaala]
    ret["raagas"] = len(raagas)
    ret["taalas"] = len(taalas)
    return ret

@user_passes_test(views.is_staff)
def carnatic(request):
    collectionid = compmusic.CARNATIC_COLLECTION

    ret = _common_stats(collectionid)
    if "missing" not in ret:
        # Only do carnatic-specific stats if we have common ones
        rata = _raaga_taala_by_results(collectionid)
        ret["raagas"] = rata["raagas"]
        ret["taalas"] = rata["taalas"]

        import carnatic
        composers = carnatic.models.Composer.objects
        ret["composers"] = composers.count()
        artists = carnatic.models.Artist.objects

        raaga_ob = carnatic.models.Raaga.objects
        taala_ob = carnatic.models.Taala.objects
        ret["raaga_objects"] = raaga_ob.count()
        ret["taala_objects"] = taala_ob.count()

        lead_artists = carnatic.models.Artist.objects.filter(instrumentperformance__lead=True).distinct()
        ret["lead_artists"] = lead_artists.count()

        leadartists = artists.annotate(Count('concert'))
        ret["lead_artists_objects"] = len([a for a in leadartists if a.concert__count > 0])


    # Duration
    return render(request, 'stats/carnatic.html', ret)

@user_passes_test(views.is_staff)
def carnatic_releases(requests):
    pass

@user_passes_test(views.is_staff)
def carnatic_artists(requests):
    pass

@user_passes_test(views.is_staff)
def carnatic_recordings(requests):
    pass

@user_passes_test(views.is_staff)
def carnatic_works(requests):
    pass


@user_passes_test(views.is_staff)
def hindustani(request):

    collectionid = compmusic.HINDUSTANI_COLLECTION

    ret = _common_stats(collectionid)
    if "missing" not in ret:
        rata = _raaga_taala_by_results(collectionid)
        ret["raagas"] = rata["raagas"]
        ret["taalas"] = rata["taalas"]

        relchecker = "dashboard.completeness.ReleaseRelationships"
        artists = set()
        composers = set()
        works = set()
        relartists = set()
        results = models.MusicbrainzReleaseResult.objects.filter(
               musicbrainzrelease__collection__id=collectionid).filter(checker__module=relchecker)
        for r in results.all():
            data = json.loads(r.data) if r.data else {}
            for a in data["releaseartistrels"]:
                artists.add(a["target"])
            for a in data["releaseleadartistrels"]:
                artists.add(a["target"])
            for a in data["artists"]:
                relartists.add(a["artist"]["id"])
                artists.add(a["artist"]["id"])
            for rec in data["recordings"]:
                for a in rec["artists"]:
                    artists.add(a["target"])
                for a in rec["leadartists"]:
                    artists.add(a["target"])
                for w in rec["works"]:
                    works.add(w["id"])
                    for c in w["composers"]:
                        composers.add(c["id"])

        ret["artists"] = len(list(artists))
        ret["composers"] = len(list(composers))
        ret["works"] = len(list(works))
        ret["releaseartists"] = len(list(relartists))
    # Duration, num lead artists
    return render(request, 'stats/hindustani.html', ret)

@user_passes_test(views.is_staff)
def makam(request):
    collectionid = compmusic.MAKAM_COLLECTION

    ret = _common_stats(collectionid)
    if "missing" not in ret:

        makamchecker = "dashboard.completeness.MakamTags"
        usuls = set()
        makams = set()
        results = models.CollectionFileResult.objects.filter(
               collectionfile__directory__musicbrainzrelease__collection__id=collectionid).filter(
               checker__module=makamchecker)
        for r in results.all():
            data = json.loads(r.data) if r.data else {}
            thismakam = data.get("makams", [])
            thisusul = data.get("usuls", [])
            [makams.add(tm) for tm in thismakam]
            [usuls.add(tu) for tu in thisusul]
        ret["makams"] = len(list(makams))
        ret["usuls"] = len(list(usuls))

        relchecker = "dashboard.completeness.ReleaseRelationships"
        artists = set()
        composers = set()
        works = set()
        relartists = set()
        results = models.MusicbrainzReleaseResult.objects.filter(
               musicbrainzrelease__collection__id=collectionid).filter(checker__module=relchecker)
        for r in results.all():
            data = json.loads(r.data) if r.data else {}
            for a in data["releaseartistrels"]:
                artists.add(a["target"])
            for a in data["releaseleadartistrels"]:
                artists.add(a["target"])
            for a in data["artists"]:
                relartists.add(a["artist"]["id"])
                artists.add(a["artist"]["id"])
            for rec in data["recordings"]:
                for a in rec["artists"]:
                    artists.add(a["target"])
                for a in rec["leadartists"]:
                    artists.add(a["target"])
                for w in rec["works"]:
                    works.add(w["id"])
                    for c in w["composers"]:
                        composers.add(c["id"])

        ret["artists"] = len(list(artists))
        ret["composers"] = len(list(composers))
        ret["works"] = len(list(works))
        ret["releaseartists"] = len(list(relartists))

    # Duration
    return render(request, 'stats/makam.html', ret)

@user_passes_test(views.is_staff)
def beijing(request):
    collectionid = compmusic.CARNATIC_COLLECTION

    releases = models.MusicbrainzRelease.objects.filter(collection__id=collectionid).all()
    ret = {}
    if len(releases):
        pass
    else:
        ret["missing"] = True
    # duration, num recordings, num albums, num singers, num arias, role-types, shengqiangs
    return render(request, 'stats/beijing.html', ret)

@user_passes_test(views.is_staff)
def andalusian(request):
    collectionid = compmusic.CARNATIC_COLLECTION

    releases = models.MusicbrainzRelease.objects.filter(collection__id=collectionid).all()
    ret = {}
    if len(releases):
        pass
    else:
        ret["missing"] = True
    # duration, num recordings, num albums, orchestras, nawbas, tabs, myazens
    return render(request, 'stats/andalusian.html', ret)
