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

from django.db import models
from django_extensions.db.fields import UUIDField
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils.text import slugify

import collections

import data.models
from carnatic import search
import managers
import filters
import random
import pysolr

class CarnaticStyle(object):
    def get_style(self):
        return "carnatic"

    def get_object_map(self, key):
        return {"performance": InstrumentPerformance,
                "release": Concert,
                "composer": Composer,
                "artist": Artist,
                "recording": Recording,
                "work": Work,
                "instrument": Instrument
                }[key]

class GeographicRegion(CarnaticStyle, models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

class MusicalSchool(CarnaticStyle, models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

class Artist(CarnaticStyle, data.models.Artist):
    state = models.ForeignKey(GeographicRegion, blank=True, null=True)
    gurus = models.ManyToManyField("Artist", related_name="students")

    def similar_artists(self):
        idset = set()
        # we are not similar to ourselves
        idset.add(self.id)
        ids = []
        gurus = []
        students = []
        siblings = []
        for g in self.gurus.all():
            # TODO: This should be inline_artist stuff
            gurus.append(g)
        for s in self.students.all():
            students.append(s)
        for g in self.gurus.all():
            for s in g.students.all():
                siblings.append((g, s))

        # sort each group by age
        ourage = int(self.begin[:4]) if self.begin else 9999
        gurus = sorted(gurus, key=lambda a: int(a.begin[:4]) if a.begin else 9999)
        students = sorted(students, key=lambda a: int(a.begin[:4]) if a.begin else 9999)
        siblings = sorted(siblings, key=lambda a: abs((int(a[1].begin[:4]) if a[1].begin else 9999) - ourage))

        for g in gurus:
            ids.append((g.id, "%s is the guru of %s" % (g.name, self.name)))
            idset.add(g.id)
        for s in students:
            if s.id not in idset:
                idset.add(s.id)
                ids.append((s.id, "%s is a student of %s" % (s.name, self.name)))
        for sib in siblings:
            guru = sib[0]
            s = sib[1]
            if s.id not in idset:
                idset.add(s.id)
                ids.append((s.id, "%s and %s share the same guru (%s)" % (self.name, s.name, guru.name)))

        return [(Artist.objects.get(pk=pk), desc) for pk, desc in ids]

    def collaborating_artists(self, collection_ids=False, permission=False):
        # Returns [ (collaborating artist, list of concerts, number of restricted concerts) ]
        #   - number of restricted concerts corresponds to the number of concerts not in the given collections
        # Get all concerts
        # For each artist on the concerts (both types), add a counter
        # top artist ids + the concerts they collaborate on
        rcollections=[]
        if collection_ids:
            rcollections = collection_ids.replace(' ','').split(",")
        if not permission:
            permission = ["U"]

        c = collections.Counter()
        concerts = collections.defaultdict(set)
        restr_concerts = collections.Counter()
        for concert in self.concerts(collection_ids=False, permission=['U','R','S']):
            # We always use collections to see if an artist is similar
            # However, if the user can't see collections, we need to say
            # `Artist a performed with b on these concerts and n more`
            for p in concert.performers():
                if p.id != self.id:
                    if collection_ids and concert.collection and concert.collection.mbid in rcollections and concert.collection.permission in permission:
                        concerts[p.id].add(concert)
                    else:
                        restr_concerts[p.id] += 1
                    c[p.id] += 1

        collaborators =  [(Artist.objects.get(pk=pk), sorted(list(concerts[pk]), key=lambda c: c.title), restr_concerts[pk]) for pk, count in c.most_common()]
        collaborators = sorted(collaborators, key=lambda c: (len(c[1])+c[2], len(c[1])), reverse=True)
        return collaborators

    def recordings(self, collection_ids=False, permission=False):
        return Recording.objects.with_permissions(collection_ids, permission).filter(Q(instrumentperformance__artist=self) | Q(concert__artists=self)).distinct()

    def concerts(self, raagas=[], taalas=[], collection_ids=False, permission=False):
        """ Get all the concerts that this artist performs in
        If `raagas` or `taalas` is set, only show concerts where
        these raagas or taalas were performed.
        If collections are received, the concerts are limited to
        that collections
        By defaul permissions are restricted to universal
        accesible collections.
        """
        rcollections=[]
        if collection_ids:
            rcollections = collection_ids.replace(' ','').split(",")
        if not permission:
            permission = ["U"]
        ret = []
        concerts = self.primary_concerts.with_permissions(collection_ids, permission)
        if raagas:
            concerts = concerts.filter(recordings__work__raaga__in=raagas)
        if taalas:
            concerts = concerts.filter(recordings__work__taala__in=taalas)
        ret.extend(concerts.all())
        for a in self.groups.all():
            for c in a.concerts(raagas, taalas):
                if c not in ret and c.collection \
                        and (collection_ids == False or c.collection.mbid in rcollections) \
                        and c.collection.permission in permission:
                    ret.append(c)
        for concert, perf in self.performances(raagas, taalas):
            if concert not in ret and concert.collection \
                    and (collection_ids == False or concert.collection.mbid in rcollections) \
                    and concert.collection.permission in permission:
                ret.append(concert)
        ret = sorted(ret, key=lambda c: c.year if c.year else 0)
        return ret

    def performances(self, raagas=[], taalas=[]):
        ReleaseClass = self.get_object_map("release")
        IPClass = self.get_object_map("performance")
        concerts = ReleaseClass.objects.filter(recordings__instrumentperformance__artist=self)
        if raagas:
            concerts = concerts.filter(recordings__work__raaga__in=raagas)
        if taalas:
            concerts = concerts.filter(recordings__work__taala__in=taalas)
        concerts = concerts.distinct()
        ret = []
        for c in concerts:
            # If the relation is on the track, we'll have lots of performances,
            # restrict the list to just one instance
            # TODO: If more than one person plays the same instrument this won't work well
            performances = IPClass.objects.filter(artist=self, recording__concert=c).distinct()
            # Unique the instrument list
            instruments = []
            theperf = []
            for p in performances:
                if p.instrument not in instruments:
                    theperf.append(p)
                    instruments.append(p.instrument)
            ret.append((c, theperf))
        return ret

    @classmethod
    def get_filter_criteria(cls):
        ret = {"url": reverse('carnatic-artist-search'),
               "name": "Artist",
               "data": [filters.School().object, filters.Region().object, filters.Generation().object]
               }
        return ret

class ArtistAlias(CarnaticStyle, data.models.ArtistAlias):
    pass

class Language(CarnaticStyle, models.Model):
    name = models.CharField(max_length=50)

    objects = managers.FuzzySearchManager()

    def __unicode__(self):
        return self.name

class LanguageAlias(CarnaticStyle, models.Model):
    name = models.CharField(max_length=50)
    language = models.ForeignKey(Language, related_name="aliases")

    objects = managers.FuzzySearchManager()

    def __unicode__(self):
        return self.name

class Sabbah(CarnaticStyle, models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

class ConcertRecording(models.Model):
    """ Links a concert to a recording with an explicit ordering """
    concert = models.ForeignKey('Concert')
    recording = models.ForeignKey('Recording')
    # The number that the track comes in the concert. Numerical 1-n
    track = models.IntegerField()
    # The disc number. 1-n
    disc = models.IntegerField()
    # The track number within this disc. 1-n
    disctrack = models.IntegerField()

    class Meta:
        ordering = ("track", )

    def __unicode__(self):
        return u"%s: %s from %s" % (self.track, self.recording, self.concert)

class Concert(CarnaticStyle, data.models.Release):
    sabbah = models.ForeignKey(Sabbah, blank=True, null=True)
    recordings = models.ManyToManyField('Recording', through="ConcertRecording")

    objects = managers.CollectionConcertManager()
    collection = models.ForeignKey('data.Collection', blank=True, null=True)

    def get_absolute_url(self):
        viewname = "%s-concert" % (self.get_style(), )
        return reverse(viewname, args=[self.mbid, slugify(self.title)])

    def tracklist(self):
        """Return an ordered list of recordings in this concert"""
        return self.recordings.order_by('concertrecording')

    def instruments_for_artist(self, artist):
        """ Returns a list of instruments that this
        artist performs on this release."""
        return Instrument.objects.filter(instrumentperformance__artist=artist).distinct()

    def performers(self):
        """ The performers on a release are those who are in the performance
        relations, and the lead artist of the release (listed first)
        """
        ret = self.artists.all()
        artists = Artist.objects.filter(instrumentperformance__recording__concert=self).exclude(id__in=ret).distinct()
        return list(ret) + list(artists)

    @classmethod
    def get_filter_criteria(cls):
        ret = {"url": reverse('carnatic-concert-search'),
               "name": "Concert",
               "data": [filters.Venue().object, filters.Instrument().object]
               }
        return ret

    def get_similar(self):

        artists = set(self.artists.all())
        for p in self.performers():
            artists.add(p)
        works = Work.objects.filter(recording__concert=self)
        raagas = Raaga.objects.filter(work__recording__concert=self)
        taalas = Taala.objects.filter(work__recording__concert=self)

        aid = [a.id for a in artists]
        wid = [w.id for w in works]
        rid = [r.id for r in raagas]
        tid = [t.id for t in taalas]

        ret = []
        try:
            similar = search.get_similar_concerts(wid, rid, tid, aid)
            similar = sorted(similar, reverse=True,
                             key=lambda c: (len(c[1]["works"]), len(c[1]["artists"]), len(c[1]["raagas"])))

            similar = similar[:10]
            for s, v in similar:
                # Don't show this concert as similar
                if s == self.id:
                    continue
                try:
                    concert = Concert.objects.get(pk=s)
                except Concert.DoesNotExist:
                    continue

                works = [Work.objects.get(pk=w) for w in v["works"]]
                raagas = [Raaga.objects.get(pk=r) for r in v["raagas"]]
                taalas = [Taala.objects.get(pk=t) for t in v["taalas"]]
                artists = [Artist.objects.get(pk=a) for a in v["artists"]]
                ret.append((concert,
                           {"works": works,
                            "raagas": raagas,
                            "taalas": taalas,
                            "artists": artists}))
        except pysolr.SolrError:
            # TODO: Should show an error message
            pass

        return ret

class RaagaAlias(models.Model):
    name = models.CharField(max_length=50)
    raaga = models.ForeignKey("Raaga", related_name="aliases")

    fuzzymanager = managers.FuzzySearchManager()
    objects = models.Manager()

    def __unicode__(self):
        return self.name

class RecordingForm(models.Model):
    """ Links a Form and a Recording with a sequence (if there is more than
        one form in the recording) """
    recording = models.ForeignKey('Recording')
    form = models.ForeignKey('Form')

    sequence = models.IntegerField()

    class Meta:
        ordering = ("sequence", )

    def __unicode__(self):
        return u"%s, seq %d %s" % (self.recording, self.sequence, self.form)

class Form(models.Model):
    name = models.CharField(max_length=50)
    attrfromrecording = models.BooleanField(default=False)

    objects = managers.CarnaticFormManager()
    fuzzymanager = managers.FuzzySearchManager()

    def __unicode__(self):
        return self.name

class FormAlias(models.Model):
    name = models.CharField(max_length=50)
    form = models.ForeignKey(Form, related_name="aliases")

    objects = managers.FuzzySearchManager()

    def __unicode__(self):
        return self.name

raaga_similar = {1: [14, 64, 159, 55, 16],
 2: [98, 207, 78, 31],
 7: [153, 265, 210, 283, 229],
 8: [265, 210, 166, 37, 32],
 9: [242, 27, 8, 265, 166],
 10: [4, 154, 60, 35, 159],
 11: [64, 14, 159, 52, 70],
 13: [10, 38, 167, 4, 15],
 14: [159, 1, 154, 64, 11, 159, 1, 154, 64, 11],
 15: [31, 52, 30, 70, 10],
 17: [55, 274, 134, 5, 47],
 21: [188, 254, 58, 9, 83],
 23: [70, 1, 14, 172, 58],
 24: [193, 164, 77, 266, 106],
 25: [81, 104, 221, 38, 262],
 27: [224, 203, 254, 9, 20, 98, 2, 78, 207, 102],
 28: [145, 184, 56, 210, 83],
 30: [52, 46, 31, 64, 15],
 31: [15, 30, 52, 14, 159],
 33: [90, 94, 28, 83, 56],
 35: [4, 10, 154, 262, 203, 4, 10, 154, 262, 203],
 36: [141, 35, 10, 4, 70, 141, 35, 10, 4, 70],
 37: [32, 220, 210, 8, 116],
 38: [10, 13, 4, 141, 167],
 44: [31, 262, 98, 52],
 46: [64, 247, 62, 210, 30],
 47: [209, 17, 68, 62, 55],
 52: [64, 15, 30, 46, 31, 46, 62, 210, 247, 83],
 55: [17, 1, 136, 274, 4],
 56: [145, 184, 28, 112, 6],
 57: [216, 137, 194, 55, 262],
 58: [174, 23, 47, 115, 40],
 60: [10, 4, 35, 124, 36, 10, 4, 35, 124, 36],
 62: [64, 46, 247, 203, 210],
 68: [47, 57, 125, 216, 187, 47, 57, 125, 216, 187],
 69: [141, 244, 120, 154, 38, 141, 244, 120, 154, 38],
 70: [159, 10, 64, 46, 31],
 73: [92, 209, 55, 17, 174, 92, 209, 55, 17, 174],
 74: [136, 55, 194, 49],
 76: [16, 14, 1, 176, 154],
 77: [17, 72, 274, 134, 216],
 80: [174, 48, 58, 275, 262],
 81: [104, 120, 25, 262, 38],
 83: [46, 52, 210, 30, 64, 27, 188, 254, 9, 21],
 85: [196, 56, 145, 184, 28, 94, 153, 229, 115, 28],
 87: [190, 166, 106, 72, 242],
 90: [33, 115, 113, 83],
 91: [159, 154, 64, 62, 46],
 92: [209, 64, 60, 1, 52],
 93: [224, 203, 266, 242, 8],
 95: [94, 254, 47, 274, 17],
 104: [81, 38, 10, 25, 262],
 111: [9, 27, 137, 274, 152],
 113: [115, 90, 48, 33, 83],
 114: [200, 5, 17, 141, 266],
 115: [94, 153, 30, 64],
 122: [248, 61, 69, 247, 148],
 124: [4, 60, 35, 10, 52],
 125: [62, 47, 52, 68],
 126: [201, 214, 27, 152, 35],
 128: [141, 4, 203, 46, 154],
 129: [38, 104, 81, 167, 13],
 131: [5, 200, 77, 17, 193],
 133: [167, 112, 56, 15, 31],
 135: [102, 148, 98, 219, 54],
 136: [55, 1, 10, 159, 4],
 137: [71, 137, 216, 254, 57],
 138: [280, 227, 23, 168, 58],
 139: [57, 68, 125, 262, 216],
 145: [28, 184, 56, 210, 8],
 146: [40, 102, 160, 153],
 148: [61, 98, 2, 14, 70],
 151: [211, 281, 36, 8, 203],
 152: [149, 20, 203, 201, 137],
 153: [229, 7, 283, 210],
 154: [159, 4, 262, 14, 141],
 156: [13, 38, 141, 244, 124],
 157: [70, 13, 36, 159, 91],
 159: [14, 154, 64, 70, 1],
 160: [99, 242, 283, 166, 37],
 164: [24, 242, 238, 93, 9],
 165: [133, 25, 237, 44],
 169: [233, 8, 93, 210, 37],
 172: [285, 14, 70, 76, 23],
 177: [207, 30, 159, 244],
 179: [68, 199, 47, 275, 125],
 181: [176, 128, 283, 141, 148],
 182: [17, 72, 274, 187, 137],
 183: [168, 23, 280, 138, 216],
 184: [28, 145, 56, 210, 229],
 185: [262, 176, 4, 154, 187],
 188: [21, 83, 9, 174, 58],
 189: [118, 112, 6, 208, 201],
 193: [71, 216, 24, 266, 77],
 196: [85, 56, 184, 145, 28],
 197: [60, 35, 4, 5, 17],
 199: [40, 28, 47, 209, 145],
 200: [5, 131, 114, 134, 17],
 201: [35, 262, 4, 208, 27, 35, 262, 4, 208, 27],
 203: [64, 141, 32, 35, 4],
 205: [14, 64, 1, 27, 224],
 207: [98, 2, 30, 154, 159],
 208: [35, 201, 203, 4, 141],
 210: [8, 64, 37, 46, 265],
 211: [110, 118, 8, 265, 166],
 213: [66, 32, 247, 14, 154],
 214: [225, 10, 201, 4, 60],
 216: [57, 55, 137, 274, 47],
 219: [78, 98, 2, 15, 31],
 220: [37, 32, 210, 8, 27],
 222: [167, 112, 6, 275, 57],
 223: [70, 30, 46, 11, 64],
 224: [242, 20, 284, 203, 93],
 225: [214, 274, 203, 10, 35],
 226: [134, 17, 106, 232, 77],
 232: [166, 106, 265, 203, 8],
 233: [37, 210, 229, 8, 32, 55, 17, 216, 187, 137],
 236: [49, 76, 176, 16, 272],
 237: [25, 31, 15, 251, 49],
 239: [140, 48, 174, 92, 206],
 240: [262, 154, 35, 185, 159],
 241: [91, 242, 20, 224, 247],
 244: [221, 154, 13, 10, 141],
 247: [46, 121, 66, 64, 62, 99, 219, 213, 283],
 254: [254, 274, 209, 166, 8, 209, 137, 254, 274, 27],
 262: [154, 35, 4, 10, 52],
 265: [8, 210, 166, 7, 283],
 266: [203, 224, 93, 72, 149],
 285: [141, 16, 159, 1, 14]}

class Raaga(data.models.BaseModel):
    missing_image = "raaga.jpg"

    name = models.CharField(max_length=50)
    common_name = models.CharField(max_length=50)
    uuid = UUIDField(db_index=True, auto=True)

    objects = managers.CarnaticRaagaManager()
    fuzzymanager = managers.FuzzySearchManager()

    def __unicode__(self):
        return self.name

    @classmethod
    def get_filter_criteria(cls):
        ret = {"url": reverse('carnatic-raaga-search'),
               "name": "Raaga",
               "data": [filters.Text().object]
               }
        return ret

    def get_absolute_url(self):
        if self.common_name:
            slug = slugify(self.common_name)
        else:
            slug = slugify(self.name)
        return reverse('carnatic-raaga', args=[str(self.uuid), slug])

    def works(self):
        return self.work_set.distinct().all()

    def composers(self):
        return Composer.objects.filter(works__raaga=self).distinct()

    def artists(self):
        artistmap = {}
        artistcounter = collections.Counter()
        artists = Artist.objects.filter(primary_concerts__recordings__work__raaga=self).filter(main_instrument__in=[1, 2])
        for a in artists:
            artistcounter[a.pk] += 1
            if a.pk not in artistmap:
                artistmap[a.pk] = a
        artists = []
        for aid, count in artistcounter.most_common():
            artists.append(artistmap[aid])
        return artists

    def get_similar(self):
        if self.pk in raaga_similar:
            sim = []
            for id in raaga_similar[self.pk]:
                try:
                    sim.append(Raaga.objects.get(pk=id))
                except Raaga.DoesNotExist:
                    pass
            return sim
        else:
            return []

    def recordings(self, limit=None):
        recordings = Recording.objects.filter(work__raaga=self)
        if recordings is not None:
            recordings = recordings[:limit]
        return recordings

    def recordings_form(self, form=None):
        ret = self.recording_set
        if form:
            ret = ret.filter(forms__name=form)
        return ret.all()

class TaalaAlias(models.Model):
    name = models.CharField(max_length=50)
    taala = models.ForeignKey("Taala", related_name="aliases")

    fuzzymanager = managers.FuzzySearchManager()
    objects = models.Manager()

    def __unicode__(self):
        return self.name


# similarity matrix. key: a taala id, val: an ordered list of similarities (taala ids)
# We fill in 'above' and 'below' the diagonal - e.g. 1: 2,3 / 2: 1
taala_similar = {1: [5], 3: [7, 11, 10], 4: [8, 9], 5: [1], 6: [2],
                 7: [3, 11, 10], 8: [4, 9], 2: [6], 9: [8, 4],
                 10: [7, 3], 11: [7, 3]}

class Taala(data.models.BaseModel):
    missing_image = "taala.jpg"

    name = models.CharField(max_length=50)
    common_name = models.CharField(max_length=50)
    num_aksharas = models.IntegerField(null=True)
    uuid = UUIDField(db_index=True, auto=True)

    objects = managers.CarnaticTaalaManager()
    fuzzymanager = managers.FuzzySearchManager()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        if self.common_name:
            slug = slugify(self.common_name)
        else:
            slug = slugify(self.name)
        return reverse('carnatic-taala', args=[str(self.uuid), slug])

    def get_similar(self):
        if self.pk in taala_similar:
            return [Taala.objects.get(pk=id) for id in taala_similar[self.pk]]
        else:
            return []

    @classmethod
    def get_filter_criteria(cls):
        ret = {"url": reverse('carnatic-taala-search'),
               "name": "Taala",
               "data": [filters.Text().object]
               }
        return ret

    def works(self):
        return self.work_set.distinct().all()

    def composers(self):
        return Composer.objects.filter(works__taala=self).distinct()

    def artists(self):
        return Artist.objects.filter(primary_concerts__recordings__work__taala=self).distinct()

    def percussion_artists(self):
        artistmap = {}
        artistcounter = collections.Counter()
        artists = Artist.objects.filter(Q(instrumentperformance__recording__work__taala=self) & Q(instrumentperformance__instrument__percussion=True))
        for a in artists:
            artistcounter[a.pk] += 1
            if a.pk not in artistmap:
                artistmap[a.pk] = a
        artists = []
        for aid, count in artistcounter.most_common():
            artists.append(artistmap[aid])
        return artists

    def recordings(self, limit=None):
        recordings = Recording.objects.filter(work__taala=self)
        if recordings is not None:
            recordings = recordings[:limit]
        return recordings

class Work(CarnaticStyle, data.models.Work):

    # (raaga, taala)
    raaga = models.ForeignKey('Raaga', blank=True, null=True)
    taala = models.ForeignKey('Taala', blank=True, null=True)
    form = models.ForeignKey('Form', blank=True, null=True)
    language = models.ForeignKey('Language', blank=True, null=True)

    @property
    def single_raaga(self):
        if self.raaga.count():
            return self.raaga.first()
        return None

    @property
    def single_taala(self):
        if self.taala.count():
            return self.taala.first()
        return None

    @classmethod
    def get_filter_criteria(cls):
        ret = {"url": reverse('carnatic-work-search'),
               "name": "Composition",
               "data": [filters.Form().object, filters.Language().object, filters.WorkDate().object]
               }
        return ret

    def recordings(self):
        return self.recording_set.all()

class RecordingRaaga(models.Model):
    recording = models.ForeignKey('Recording')
    raaga = models.ForeignKey('Raaga')
    sequence = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return u"%s, seq %d %s" % (self.recording, self.sequence, self.raaga)

class RecordingTaala(models.Model):
    recording = models.ForeignKey('Recording')
    taala = models.ForeignKey('Taala')
    sequence = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return u"%s, seq %d %s" % (self.recording, self.sequence, self.taala)

class WorkRaaga(models.Model):
    work = models.ForeignKey('Work')
    raaga = models.ForeignKey('Raaga')
    sequence = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return u"%s, seq %d %s" % (self.work, self.sequence, self.raaga)

class WorkTaala(models.Model):
    work = models.ForeignKey('Work')
    taala = models.ForeignKey('Taala')
    sequence = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return u"%s, seq %d %s" % (self.work, self.sequence, self.taala)

class RecordingWork(models.Model):
    recording = models.ForeignKey('Recording')
    work = models.ForeignKey('Work')
    sequence = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return u"%s, seq %d %s" % (self.recording, self.sequence, self.work)

class Recording(CarnaticStyle, data.models.Recording):
    # TODO: To remove
    work = models.ForeignKey('Work', blank=True, null=True, related_name='single_work')

    works = models.ManyToManyField('Work', through='RecordingWork')
    forms = models.ManyToManyField('Form', through='RecordingForm')

    raagas = models.ManyToManyField('Raaga', through='RecordingRaaga')
    taalas = models.ManyToManyField('Taala', through='RecordingTaala')

    objects = managers.CollectionRecordingManager()

    #def raaga(self):
    #    if self.work:
    #        rs = self.work.raaga.all()
    #        if rs:
    #            return rs[0]
    #    return None

    #def taala(self):
    #    if self.work:
    #        ts = self.work.taala.all()
    #        if ts:
    #            return ts[0]
    #    return None

    def all_artists(self):
        ArtistClass = self.get_object_map("artist")
        primary_artists = ArtistClass.objects.filter(primary_concerts__recordings=self)

        IPClass = self.get_object_map("performance")
        recperfs = IPClass.objects.filter(recording=self)
        rec_artists = [r.artist for r in recperfs]

        all_as = set(primary_artists) | set(rec_artists)
        return list(all_as)

    def is_restricted(self):
        for rel in self.concert_set.filter(collection__permission__in=["S"]).all():
            return True
        return False

class InstrumentAlias(CarnaticStyle, data.models.InstrumentAlias):
    fuzzymanager = managers.FuzzySearchManager()
    objects = models.Manager()

class Instrument(CarnaticStyle, data.models.Instrument):
    fuzzymanager = managers.FuzzySearchManager()
    objects = managers.CarnaticInstrumentManager()

    def description(self):
        return "The description of an instrument"

    def ordered_performers(self):
        perfs, counts = self.performers()
        perfs = sorted(perfs, key=lambda p: counts[p.artist], reverse=True)
        return [p.artist for p in perfs]

    def performers(self):
        IPClass = self.get_object_map("performance")
        performances = IPClass.objects.filter(instrument=self).distinct()
        ret = []
        artists = []
        # Sort how many performances this artist makes
        artistcount = collections.Counter()
        for p in performances:
            artistcount[p.artist] += 1
            if p.artist not in artists:
                ret.append(p)
                artists.append(p.artist)

        return ret, artistcount

    def references(self):
        pass

    def samples(self, limit=2):
        IPClass = self.get_object_map("performance")
        performances = list(IPClass.objects.filter(instrument=self).all())
        random.shuffle(performances)
        perf = performances[:limit]
        return [p.recording for p in perf]

    @classmethod
    def get_filter_criteria(cls):
        ret = {"url": reverse('carnatic-instrument-search'),
               "name": "Instrument",
               "data": [filters.Text().object]
               }
        return ret

class InstrumentPerformance(CarnaticStyle, data.models.InstrumentPerformance):
    pass

class Composer(CarnaticStyle, data.models.Composer):
    state = models.ForeignKey(GeographicRegion, blank=True, null=True)

    def raagas(self):
        return Raaga.objects.filter(work__composer=self).all()

    def taalas(self):
        return Taala.objects.filter(work__composer=self).all()

class ComposerAlias(CarnaticStyle, data.models.ComposerAlias):
    pass
