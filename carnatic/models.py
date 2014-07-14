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
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils.text import slugify

import collections

import data.models
from carnatic import search
import managers
import filters
import random
import docserver
import pysolr

class CarnaticStyle(object):
    def get_style(self):
        return "carnatic"
    def get_object_map(self, key):
        return {"performance": InstrumentPerformance,
                "releaseperformance": InstrumentConcertPerformance,
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
        siblings = sorted(siblings, key=lambda a: abs((int(a[1].begin[:4]) if a[1].begin else 9999)-ourage))

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

    def collaborating_artists(self):
        # Get all concerts
        # For each artist on the concerts (both types), add a counter
        # top 10 artist ids + the concerts they collaborate on
        c = collections.Counter()
        concerts = collections.defaultdict(set)
        for concert in self.concerts():
            for p in concert.performers():
                thea = p.performer
                if thea.id != self.id:
                    concerts[thea.id].add(concert)
                    c[thea.id] += 1

        return [(Artist.objects.get(pk=pk), list(concerts[pk])) for pk,count in c.most_common()]

    def concerts(self, raagas=[], taalas=[]):
        """ Get all the concerts that this artist performs in
        If `raagas` or `taalas` is set, only show concerts where
        these raagas or taalas were performed.
        """
        ret = []
        concerts = self.primary_concerts
        if raagas:
            concerts = concerts.filter(tracks__work__raaga__in=raagas)
        if taalas:
            concerts = concerts.filter(tracks__work__taala__in=taalas)
        ret.extend(concerts.all())
        for a in self.groups.all():
            ret.extend([c for c in a.concerts(raagas, taalas) if c not in ret])
        for concert, perf in self.performances(raagas, taalas):
            if concert not in ret:
                ret.append(concert)
        ret = sorted(ret, key=lambda c: c.year if c.year else 0)
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
    """ Links a concert to a recording with an implicit ordering """
    concert = models.ForeignKey('Concert')
    recording = models.ForeignKey('Recording')
    # The number that the track comes in the concert. Numerical 1-n
    track = models.IntegerField()

    def __unicode__(self):
        return u"%s: %s from %s" % (self.track, self.recording, self.concert)

class Concert(CarnaticStyle, data.models.Release):
    sabbah = models.ForeignKey(Sabbah, blank=True, null=True)
    tracks = models.ManyToManyField('Recording', through="ConcertRecording")
    performance = models.ManyToManyField('Artist', through="InstrumentConcertPerformance", related_name='accompanying_concerts')

    def get_absolute_url(self):
        viewname = "%s-concert" % (self.get_style(), )
        return reverse(viewname, args=[self.mbid, slugify(self.title)])

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
            artists.add(p.performer)
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
                concert = Concert.objects.get(pk=s)
                works = [Work.objects.get(pk=w) for w in v["works"]]
                raagas = [Raaga.objects.get(pk=r) for r in v["raagas"]]
                taalas = [Taala.objects.get(pk=t) for t in v["taalas"]]
                artists = [Artist.objects.get(pk=a) for a in v["artists"]]
                ret.append((concert,
                    {"works": works, "raagas": raagas, "taalas": taalas, "artists": artists}))
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

class Form(models.Model):
    name = models.CharField(max_length=50)

    objects = managers.CarnaticFormManager()
    fuzzymanager = managers.FuzzySearchManager()

    def __unicode__(self):
        return self.name

class FormAlias(models.Model):
    name = models.CharField(max_length=50)
    form = models.ForeignKey(Form, related_name="aliases")

    fuzzymanager = managers.FuzzySearchManager()

    def __unicode__(self):
        return self.name

raaga_similar = {1: [14, 26, 55], 2: [207, 88, 31], 7: [153, 39, 29], 8: [39, 29, 37], 9: [27, 8, 39], 10: [50, 60, 35, 26], 11: [14, 26, 52, 235], 13: [10, 38, 15], 14: [26, 1, 50, 11], 15: [31, 52, 30, 235, 10], 17: [55, 47], 19: [216, 24, 155, 77], 21: [188, 191, 58, 9, 130], 22: [28, 145, 56, 29], 23: [1, 14, 172, 58], 24: [19, 164, 77, 155], 25: [81, 104, 38, 34], 26: [14, 50, 235, 1], 27: [224, 203, 191, 9], 28: [145, 22, 56, 29, 83], 29: [8, 37, 46, 39], 30: [52, 46, 31, 15], 31: [15, 30, 52, 14, 26], 33: [90, 28, 83, 56], 34: [50, 35, 10, 52], 35: [10, 50, 34, 203], 36: [35, 10, 235], 37: [220, 29, 8], 38: [10, 13], 39: [8, 29, 7], 44: [31, 34, 52], 46: [247, 230, 29, 30], 47: [17, 68, 230, 55], 50: [26, 34, 14], 52: [15, 30, 46, 31], 53: [55, 1, 10, 26], 55: [17, 1, 53], 56: [145, 22, 28], 57: [216, 55, 34], 58: [23, 47, 115], 60: [10, 35, 124, 36], 68: [47, 57, 125, 216], 69: [244, 50, 38], 73: [92, 55, 17], 74: [53, 55, 234], 76: [14, 1, 50], 77: [17, 216], 80: [58, 34], 81: [104, 25, 34, 38], 83: [46, 52, 29, 30], 85: [196, 56, 145, 22, 28], 87: [], 88: [2, 207], 90: [33, 115, 113, 83, 109], 91: [26, 50, 230, 46], 92: [60, 1, 52], 93: [224, 203, 155, 8], 95: [191, 47, 17], 104: [81, 38, 10, 25, 34], 109: [153, 115, 28], 111: [9, 27, 152], 113: [115, 90, 33, 83], 114: [200, 17, 155], 115: [153, 109, 30], 122: [69, 243, 148], 123: [46, 230, 29, 247, 83], 124: [60, 35, 10, 52], 125: [230, 47, 52, 123, 68], 126: [201, 214, 27, 152, 35], 128: [203, 46, 50], 129: [38, 104, 81, 13], 130: [27, 188, 191, 9, 21], 131: [200, 77, 17, 19], 133: [56, 15, 31], 135: [148, 219], 137: [216, 191, 57], 138: [23, 58], 139: [57, 68, 125, 34, 216], 145: [28, 22, 56, 29, 8], 146: [123, 160, 153], 148: [2, 14], 150: [191, 8], 151: [211, 36, 8, 203], 152: [203, 201], 153: [7, 109, 29], 155: [203, 224, 93], 156: [13, 38, 244, 124], 157: [235, 13, 36, 26, 91], 160: [37], 164: [24, 93, 9], 165: [133, 25, 237, 88, 44], 169: [233, 8, 93, 29, 37], 172: [192, 14, 76, 23], 177: [207, 30, 26, 244], 179: [68, 199, 47, 125], 181: [128, 148], 182: [17], 183: [23, 138, 216], 185: [34, 50], 188: [21, 130, 9, 58], 189: [208, 201], 191: [150, 27], 192: [26, 1, 14], 196: [85, 56, 22, 145, 28], 197: [60, 35, 17], 199: [28, 47, 145], 200: [131, 114, 17], 201: [35, 34, 208, 27], 203: [35], 205: [14, 1, 27, 224], 207: [2, 30, 50, 26], 208: [35, 201, 203], 211: [8, 39], 213: [247, 14, 50], 214: [225, 10, 201, 60], 216: [57, 55, 47], 219: [2, 15, 31], 220: [37, 29, 8, 27], 222: [57], 223: [235, 30, 46, 11], 224: [203, 93], 225: [214, 203, 10, 35], 226: [17, 232, 77], 230: [46, 247, 203, 29], 232: [39, 203, 8], 233: [37, 29, 8], 234: [55, 17, 216], 235: [26, 10, 46, 31], 236: [76], 237: [25, 31, 15], 239: [92], 240: [34, 50, 35, 185, 26], 241: [91, 224, 247], 243: [219, 213, 123], 244: [50, 13, 10], 247: [46, 230]}

class Raaga(data.models.BaseModel):
    missing_image = "raaga.jpg"

    name = models.CharField(max_length=50)
    common_name = models.CharField(max_length=50)

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
        return reverse('carnatic-raaga', args=[str(self.id), slugify(self.common_name)])

    def works(self):
        return self.work_set.distinct().all()

    def composers(self):
        return Composer.objects.filter(works__raaga=self).distinct()

    def artists(self):
        artistmap = {}
        artistcounter = collections.Counter()
        artists = Artist.objects.filter(primary_concerts__tracks__work__raaga=self).filter(main_instrument__in=[1,2])
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
            for id in raaga_similar[self.pk]:
                sim = []
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
        7: [3, 11, 10], 8: [4, 9], 2: [6], 9: [8, 4], 10: [7, 3], 11: [7, 3]}

class Taala(data.models.BaseModel):
    missing_image = "taala.jpg"

    name = models.CharField(max_length=50)
    common_name = models.CharField(max_length=50)
    num_aksharas = models.IntegerField(null=True)

    objects = managers.CarnaticTaalaManager()
    fuzzymanager = managers.FuzzySearchManager()

    def __unicode__(self):
        return self.name

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

    def get_absolute_url(self):
        return reverse('carnatic-taala', args=[str(self.id), slugify(self.common_name)])

    def works(self):
        return self.work_set.distinct().all()

    def composers(self):
        return Composer.objects.filter(works__taala=self).distinct()

    def artists(self):
        return Artist.objects.filter(primary_concerts__tracks__work__taala=self).distinct()

    def percussion_artists(self):
        artistmap = {}
        artistcounter = collections.Counter()
        artists = Artist.objects.filter(Q(instrumentconcertperformance__concert__tracks__work__taala=self) & Q(instrumentconcertperformance__instrument__percussion=True))
        for a in artists:
            artistcounter[a.pk] += 1
            if a.pk not in artistmap:
                artistmap[a.pk] = a
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
    raaga = models.ManyToManyField('Raaga', through="WorkRaaga")
    taala = models.ManyToManyField('Taala', through="WorkTaala")
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

class Recording(CarnaticStyle, data.models.Recording):
    work = models.ForeignKey('Work', blank=True, null=True)

    def raaga(self):
        if self.work:
            rs = self.work.raaga.all()
            if rs:
                return rs[0]
        return None

    def taala(self):
        if self.work:
            ts = self.work.taala.all()
            if ts:
                return ts[0]
        return None

    def all_artists(self):
        ArtistClass = self.get_object_map("artist")
        primary_artists = ArtistClass.objects.filter(primary_concerts__tracks=self)

        IPClass = self.get_object_map("performance")
        IRPClass = self.get_object_map("releaseperformance")
        recperfs = IPClass.objects.filter(recording=self)
        rec_artists = [r.performer for r in recperfs]
        releaseperfs = IRPClass.objects.filter(concert__tracks=self)
        release_artists = [r.performer for r in releaseperfs]

        all_as = set(primary_artists) | set(rec_artists) | set(release_artists)
        return list(all_as)



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
        perfs = sorted(perfs, key=lambda p: counts[p.performer], reverse=True)
        return perfs

    def performers(self):
        IPClass = self.get_object_map("performance")
        performances = IPClass.objects.filter(instrument=self).distinct()
        ret = []
        artists = []
        # Sort how many performances this artist makes
        artistcount = collections.Counter()
        for p in performances:
            artistcount[p.performer] += 1
            if p.performer not in artists:
                ret.append(p)
                artists.append(p.performer)

        # TODO: This might be slow getting 2 sets of performances and doing tests
        ICPClass = self.get_object_map("releaseperformance")
        performances = ICPClass.objects.filter(instrument=self).distinct()
        for p in performances:
            artistcount[p.performer] += 1
            if p.performer not in artists:
                ret.append(p)
                artists.append(p.performer)

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

class InstrumentConcertPerformance(models.Model):
    # TODO: This should be 'release' over all music types
    concert = models.ForeignKey('Concert')
    performer = models.ForeignKey('Artist')
    instrument = models.ForeignKey('Instrument')
    lead = models.BooleanField(default=False)

    def __unicode__(self):
        return u"%s playing %s in %s" % (self.performer, self.instrument, self.concert)

class Composer(CarnaticStyle, data.models.Composer):
    state = models.ForeignKey(GeographicRegion, blank=True, null=True)
    def raagas(self):
        return Raaga.objects.filter(work__composer=self).all()

    def taalas(self):
        return Taala.objects.filter(work__composer=self).all()

class ComposerAlias(CarnaticStyle, data.models.ComposerAlias):
    pass
