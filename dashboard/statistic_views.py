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

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count

from dashboard import models
from dashboard import views
import docserver
import carnatic
import hindustani

import json
import collections
import compmusic

def _common_stats(collectionid):
    """ Get some common statistics for all styles """
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
    # TODO: Only get the most rest CollectionFileResult for each file
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
def carnatic_stats(request):
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
        ret["artists"] = artists.count()

        raaga_ob = carnatic.models.Raaga.objects
        taala_ob = carnatic.models.Taala.objects
        ret["raaga_objects"] = raaga_ob.count()
        ret["taala_objects"] = taala_ob.count()

        lead_artists = carnatic.models.Artist.objects.filter(instrumentperformance__lead=True).distinct()
        ret["lead_artists"] = lead_artists.count()

        leadartists = artists.annotate(Count('primary_concerts'))
        ret["lead_artists_objects"] = len([a for a in leadartists if a.primary_concerts__count > 0])


    # Duration
    return render(request, 'stats/carnatic.html', ret)

@user_passes_test(views.is_staff)
def carnatic_releases(request):
    dashcoll = models.Collection.objects.get(id=compmusic.CARNATIC_COLLECTION)
    checker = "dashboard.completeness.CorrectMBID"
    unmatchedreleases = {}
    for dashrel in dashcoll.musicbrainzrelease_set.all():
        results = dashrel.musicbrainzreleaseresult_set.filter(checker__module=checker)
        if results:
            lastresult = results[0]
            if lastresult.result == 'b': # Bad
                data = json.loads(lastresult.data)
                unmatched = data.get("unmatchedmb", {})
                if unmatched:
                    if dashrel not in unmatchedreleases:
                        unmatchedreleases[dashrel] = []
                    unmatchedreleases[dashrel].extend(unmatched.values())

    ret = {"unmatched": unmatchedreleases}
    return render(request, 'stats/carnatic_releases.html', ret)

@user_passes_test(views.is_staff)
def carnatic_coverart(request):
    releases = carnatic.models.Concert.objects.select_related('artists')
    counted = releases.annotate(Count('images'))
    noimages = [r for r in counted.all() if r.images__count == 0]
    dashcoll = models.Collection.objects.get(id=compmusic.CARNATIC_COLLECTION)
    checker = "dashboard.completeness.ReleaseCoverart"
    nocaa = []
    relids = [r.mbid for r in counted.all() if r.images__count > 0]
    for dashrel in dashcoll.musicbrainzrelease_set.filter(mbid__in=relids):
        results = dashrel.musicbrainzreleaseresult_set.filter(checker__module=checker)
        if results:
            lastresult = results[0]
            if lastresult.result == 'b': # Bad
                nocaa.append(counted.get(mbid=dashrel.mbid))

    noimageids = [r.mbid for r in noimages]
    dashnoimage = dashcoll.musicbrainzrelease_set.filter(mbid__in=noimageids)

    noi = []
    for m, d in zip(noimages, dashnoimage):
        noi.append({"model": m, "dashboard": d})

    ret = {"noimages": noi, "nocaa": nocaa}
    return render(request, 'stats/carnatic_coverart.html', ret)

@user_passes_test(views.is_staff)
def carnatic_artists(request):
    artists = carnatic.models.Artist.objects
    image_counted = artists.annotate(Count('images'))
    bio_counted = artists.annotate(Count('description'))
    noimages = [a for a in image_counted.order_by("name").all() if a.images__count == 0]
    nobiographies = [a for a in bio_counted.order_by("name").all() if a.description__count == 0]
    noinstrument = [a for a in bio_counted.order_by("name").all() if not a.main_instrument]

    ret = {"noimages": noimages,
           "nobios": nobiographies,
           "noinstrument": noinstrument,
           "all": artists.order_by('name').all()}
    return render(request, 'stats/carnatic_artists.html', ret)

@user_passes_test(views.is_staff)
def carnatic_recordings(request):
    # TODO: Also make sure rels are on tracks not album (preferred)
    # TODO: Also check there is at least one 'lead' performer

    concerts = carnatic.models.Concert.objects.all()
    badconcerts = []
    for c in concerts:
        got_works = True
        got_track_perf = True
        got_perf = True
        for t in c.tracks.all():
            if not t.work:
                got_works = False
            if t.performance.count() == 0:
                got_track_perf = False
        if c.performance.count() == 0:
            got_perf = False
        c.got_track_perf = got_track_perf
        c.got_works = got_works
        c.got_perf = got_perf and got_track_perf

        # Artists who are the primary artist of a release, but are not listed
        # as a relationship on the release or any tracks.
        # Note that this will incorrectly select groups where group members are listed
        artists = c.artists.all()
        perf = c.instrumentconcertperformance_set.filter(performer__in=artists)
        tperf = carnatic.models.InstrumentPerformance.objects.filter(
                recording__concert=c, performer__in=artists)
        if not perf.exists() and not tperf.exists():
            c.missing_rel_artists = True

        if not c.got_works or not c.got_perf or c.missing_rel_artists:
            badconcerts.append(c)

    ret = {"concerts": badconcerts,
            }
    return render(request, 'stats/carnatic_recordings.html', ret)

@user_passes_test(views.is_staff)
def carnatic_raagataala(request):
    recordings = carnatic.models.Recording.objects

    dashcoll = models.Collection.objects.get(id=compmusic.CARNATIC_COLLECTION)
    dashfiles = models.CollectionFile.objects.filter(directory__collection=dashcoll)
    checker = "dashboard.completeness.RaagaTaalaFile"
    missingr = []
    missingt = []
    no_r = []
    no_t = []
    for f in dashfiles:
        checks = f.collectionfileresult_set.filter(checker__module=checker).order_by('-datetime')
        if len(checks):
            check = checks[0]
            data = json.loads(check.data) if check.data else {}
            if "missingt" in data:
                missingt.append({"taalas": data.get("missingt"), "file": check.collectionfile})
            if "missingr" in data:
                missingr.append({"raagas": data.get("missingr"), "file": check.collectionfile})
            if len(data["raaga"]) == 0:
                no_r.append(check.collectionfile)
            if len(data["taala"]) == 0:
                no_t.append(check.collectionfile)

    ret = { "no_r": no_r,
            "no_t": no_t,
            "missingr": missingr,
            "missingt": missingt
            }
    return render(request, 'stats/carnatic_raagataala.html', ret)

@user_passes_test(views.is_staff)
def carnatic_works(request):
    works = carnatic.models.Work.objects
    composer_counted = works.annotate(Count('composers'))
    nocomposer = [w for w in composer_counted if w.composers__count == 0]
    duplicatecomposer = [w for w in composer_counted if w.composers__count > 1]
    ret = {"nocomposer": nocomposer, 
           "duplicatecomposer": duplicatecomposer,
           "all": works.order_by('title').all()}
    return render(request, 'stats/carnatic_works.html', ret)


@user_passes_test(views.is_staff)
def hindustani_stats(request):

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
def hindustani_releases(request):
    dashcoll = models.Collection.objects.get(id=compmusic.HINDUSTANI_COLLECTION)
    checker = "dashboard.completeness.CorrectMBID"
    unmatchedreleases = {}
    for dashrel in dashcoll.musicbrainzrelease_set.all():
        results = dashrel.musicbrainzreleaseresult_set.filter(checker__module=checker)
        if results:
            lastresult = results[0]
            if lastresult.result == 'b': # Bad
                data = json.loads(lastresult.data)
                unmatched = data.get("unmatchedmb", {})
                if unmatched:
                    if dashrel not in unmatchedreleases:
                        unmatchedreleases[dashrel] = []
                    unmatchedreleases[dashrel].extend(unmatched.values())

    ret = {"unmatched": unmatchedreleases}
    return render(request, 'stats/hindustani_releases.html', ret)

@user_passes_test(views.is_staff)
def hindustani_artists(request):
    artists = hindustani.models.Artist.objects
    image_counted = artists.annotate(Count('images'))
    bio_counted = artists.annotate(Count('description'))
    noimages = [a for a in image_counted.order_by("name").all() if a.images__count == 0]
    nobiographies = [a for a in bio_counted.order_by("name").all() if a.description__count == 0]
    noinstrument = [a for a in bio_counted.order_by("name").all() if not a.main_instrument]

    ret = {"noimages": noimages,
           "nobios": nobiographies,
           "noinstrument": noinstrument,
           "all": artists.order_by('name').all()}
    return render(request, 'stats/hindustani_artists.html', ret)

@user_passes_test(views.is_staff)
def hindustani_recordings(request):
    # TODO: Also make sure rels are on tracks not album (preferred)
    # TODO: Also check there is at least one 'lead' performer

    releases = hindustani.models.Release.objects.all()
    badreleases = []
    for r in releases:
        got_works = True
        got_track_perf = True
        got_perf = True
        for t in r.tracks.all():
            if not t.works.exists():
                got_works = False
            if t.performance.count() == 0:
                got_track_perf = False
        r.got_perf = got_track_perf
        r.got_works = got_works

        # Artists who are the primary artist of a release, but are not listed
        # as a relationship on the release or any tracks.
        # Note that this will incorrectly select groups where group members are listed
        artists = r.artists.all()
        tperf = hindustani.models.InstrumentPerformance.objects.filter(
                recording__release=r, performer__in=artists)
        r.missing_rel_artists = False
        if not tperf.exists():
            r.missing_rel_artists = True

        if not r.got_works or not r.got_perf or r.missing_rel_artists:
            badreleases.append(r)

    ret = {"releases": badreleases,
            }
    return render(request, 'stats/hindustani_recordings.html', ret)

@user_passes_test(views.is_staff)
def hindustani_raagtaal(request):
    recordings = hindustani.models.Recording.objects

    dashcoll = models.Collection.objects.get(id=compmusic.HINDUSTANI_COLLECTION)
    dashfiles = models.CollectionFile.objects.filter(directory__collection=dashcoll)
    checker = "dashboard.completeness.HindustaniRaagTaal"
    missingr = []
    missingt = []
    missingf = []
    missingl = []
    no_r = {}
    no_t = {}
    no_f = {}
    no_l = {}
    for f in dashfiles:
        checks = f.collectionfileresult_set.filter(checker__module=checker).order_by('-datetime')
        if len(checks):
            check = checks[0]
            mbid = check.collectionfile.recordingid
            data = json.loads(check.data) if check.data else {}
            if "missingt" in data:
                missingt.append({"taals": data.get("missingt"), "file": check.collectionfile})
            if "missingr" in data:
                missingr.append({"raags": data.get("missingr"), "file": check.collectionfile})
            if "missingf" in data:
                missingf.append({"forms": data.get("missingf"), "file": check.collectionfile})
            if "missingl" in data:
                missingl.append({"layas": data.get("missingl"), "file": check.collectionfile})
            if len(data["raag"]) == 0:
                no_r[mbid] = check.collectionfile
            if len(data["taal"]) == 0:
                no_t[mbid] = check.collectionfile
            if len(data["form"]) == 0:
                no_f[mbid] = check.collectionfile
            if len(data["laya"]) == 0:
                no_l[mbid] = check.collectionfile

    dirs = collections.defaultdict(lambda: collections.defaultdict(dict))
    for m, r in no_r.items():
        rel = r.directory.musicbrainzrelease
        dirs[rel][r]["raag"] = True
    for m, t in no_t.items():
        rel = t.directory.musicbrainzrelease
        dirs[rel][t]["taal"] = True
    for m, l in no_l.items():
        rel = l.directory.musicbrainzrelease
        dirs[rel][l]["laya"] = True
    for m, f in no_f.items():
        rel = f.directory.musicbrainzrelease
        dirs[rel][f]["form"] = True

    # convert back from defaultdict to dict for django
    dirs = dict(dirs)
    for k, v in dirs.items():
        dirs[k] = dict(v)

    ret = { "missingr": missingr,
            "missingt": missingt,
            "missingf": missingf,
            "missingl": missingl,
            "dirs": dirs
            }
    return render(request, 'stats/hindustani_raagtaal.html', ret)

@user_passes_test(views.is_staff)
def hindustani_works(request):
    works = hindustani.models.Work.objects
    composer_counted = works.annotate(Count('composers'))
    nocomposer = [w for w in composer_counted if w.composers__count == 0]
    duplicatecomposer = [w for w in composer_counted if w.composers__count > 1]
    ret = {"nocomposer": nocomposer, 
           "duplicatecomposer": duplicatecomposer,
           "all": works.order_by('title').all()}
    return render(request, 'stats/hindustani_works.html', ret)


@user_passes_test(views.is_staff)
def makam_stats(request):
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
def beijing_stats(request):
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
def andalusian_stats(request):
    collectionid = compmusic.CARNATIC_COLLECTION

    releases = models.MusicbrainzRelease.objects.filter(collection__id=collectionid).all()
    ret = {}
    if len(releases):
        pass
    else:
        ret["missing"] = True
    # duration, num recordings, num albums, orchestras, nawbas, tabs, myazens
    return render(request, 'stats/andalusian.html', ret)
