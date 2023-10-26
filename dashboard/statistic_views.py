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

import compmusic
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count
from django.shortcuts import render

import carnatic.models
import hindustani.models
import makam.models
from dashboard import models
from dashboard import views


def _common_stats(collectionid):
    """ Get some common statistics for all styles """
    releases = models.MusicbrainzRelease.objects.filter(collection__collectionid=collectionid)
    ret = {}
    if releases.count():
        total_releases = releases.count()
        releases_ignored = releases.filter(ignore=True).count()
        counts = releases.annotate(Count('collectiondirectory'))
        releases_missing_dir = len([r for r in counts if r.collectiondirectory__count == 0])
        ret["releases"] = total_releases
        ret["releases_ignored"] = releases_ignored
        ret["releases_missing"] = releases_missing_dir

        num_recordings = models.CollectionFile.objects.filter(
            directory__musicbrainzrelease__collection__collectionid=collectionid).count()
        ret["recordings"] = num_recordings
    else:
        ret["missing"] = True
    return ret


@user_passes_test(views.is_staff)
def carnatic_stats(request):
    collectionid = compmusic.CARNATIC_COLLECTION

    ret = _common_stats(collectionid)

    # Duration
    return render(request, 'stats/carnatic.html', ret)


@user_passes_test(views.is_staff)
def carnatic_artists(request):
    artists = carnatic.models.Artist.objects
    bio_counted = artists.annotate(Count('description'))
    noimages = [a for a in artists.order_by("name").all() if a.image is None]
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
        c.missing_rel_artists = False
        got_works = True
        got_track_perf = True
        for t in c.recordings.all():
            if not len(t.works.all()):
                got_works = False
            if t.performance.count() == 0:
                got_track_perf = False
        c.got_track_perf = got_track_perf
        c.got_works = got_works

        # Artists who are the primary artist of a release, but are not listed
        # as a relationship on the release or any tracks.
        # Note that this will incorrectly select groups where group members are listed
        artists = c.artists.all()
        tperf = carnatic.models.InstrumentPerformance.objects.filter(
            recording__concert=c, artist__in=artists)
        if not tperf.exists():
            c.missing_rel_artists = True

        if not c.got_works or c.missing_rel_artists:
            badconcerts.append(c)

    ret = {"concerts": badconcerts,
           }
    return render(request, 'stats/carnatic_recordings.html', ret)


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
def carnatic_workraagataala(request):
    works = carnatic.models.Work.objects
    raaga_counted = works.annotate(Count('raaga'))
    manyraaga = [w for w in raaga_counted if w.raaga__count > 1]
    taala_counted = works.annotate(Count('taala'))
    manytaala = [w for w in taala_counted if w.taala__count > 1]
    ret = {"manyraaga": manyraaga, "manytaala": manytaala}
    return render(request, 'stats/carnatic_workraagataala.html', ret)


@user_passes_test(views.is_staff)
def hindustani_stats(request):

    collectionid = compmusic.HINDUSTANI_COLLECTION

    ret = _common_stats(collectionid)
    # Duration, num lead artists
    return render(request, 'stats/hindustani.html', ret)


@user_passes_test(views.is_staff)
def hindustani_artists(request):
    artists = hindustani.models.Artist.objects
    bio_counted = artists.annotate(Count('description'))
    noimages = [a for a in artists.order_by("name").all() if a.image is None]
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
        for t in r.recordings.all():
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
            recording__release=r, artist__in=artists)
        r.missing_rel_artists = False
        if not tperf.exists():
            r.missing_rel_artists = True

        if not r.got_works or not r.got_perf or r.missing_rel_artists:
            badreleases.append(r)

    ret = {"releases": badreleases,
           }
    return render(request, 'stats/hindustani_recordings.html', ret)


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

    # Duration
    return render(request, 'stats/makam.html', ret)


@user_passes_test(views.is_staff)
def makam_works(request):
    works = makam.models.Work.objects
    composer_counted = works.annotate(Count('composers'))
    nocomposer = [w for w in composer_counted if w.composers__count == 0]
    ret = {"nocomposer": nocomposer,
           "all": works.order_by('title').all()}
    return render(request, 'stats/makam_works.html', ret)


@user_passes_test(views.is_staff)
def makam_artists(request):
    ret = {"all": makam.models.Artist.objects.order_by('name').all()}
    return render(request, 'stats/makam_artists.html', ret)


@user_passes_test(views.is_staff)
def beijing_stats(request):
    collectionid = compmusic.CARNATIC_COLLECTION

    releases = models.MusicbrainzRelease.objects.filter(collection__collectionid=collectionid).all()
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
    ret = _common_stats(collectionid)
    releases = models.MusicbrainzRelease.objects.filter(collection__collectionid=collectionid).all()

    if len(releases):
        pass
    else:
        ret["missing"] = True
    # duration, num recordings, num albums, orchestras, nawbas, tabs, myazens
    return render(request, 'stats/andalusian.html', ret)
