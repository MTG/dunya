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

import collections
import random

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Count
from django.db.models import Q
from django.utils.text import slugify

import data.models
import managers


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


class Artist(CarnaticStyle, data.models.Artist):

    # Automatically gets the Artist + the artists' main instrument
    objects = managers.ArtistManager()

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
        rcollections = []
        if collection_ids:
            rcollections = collection_ids.replace(' ', '').split(",")
        if not permission:
            permission = ["U"]

        c = collections.Counter()
        concerts = collections.defaultdict(set)
        restr_concerts = collections.Counter()
        for concert in self.concerts(collection_ids=False, permission=['U', 'R', 'S']):
            # We always use collections to see if an artist is similar
            # However, if the user can't see collections, we need to say
            # `Artist a performed with b on these concerts and n more`
            for p in concert.performers():
                if p.id != self.id:
                    if collection_ids and concert.collection and str(concert.collection.collectionid) in rcollections and concert.collection.permission in permission:
                        concerts[p.id].add(concert)
                    else:
                        restr_concerts[p.id] += 1
                    c[p.id] += 1

        collaborators = [(Artist.objects.get(pk=pk), sorted(list(concerts[pk]), key=lambda c: c.title), restr_concerts[pk]) for pk, count in c.most_common()]
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
        rcollections = []
        if collection_ids:
            rcollections = collection_ids.replace(' ', '').split(",")
        if not permission:
            permission = ["U"]

        ret = []
        concerts = self.primary_concerts.with_permissions(collection_ids, permission)
        if raagas:
            concerts = concerts.filter(Q(recordings__works__raaga__in=raagas)|Q(recordings__raagas__in=raagas)).distinct()
        if taalas:
            concerts = concerts.filter(Q(recordings__works__taala__in=taalas)|Q(recordings__taalas__in=taalas)).distinct()
        ret.extend(concerts.all())
        for a in self.groups.all():
            for c in a.concerts(raagas, taalas):
                if c not in ret and c.collection \
                        and (collection_ids is False or str(c.collection.collectionid) in rcollections) \
                        and c.collection.permission in permission:
                    ret.append(c)
        for concert, perf in self.performances(raagas, taalas):
            if concert not in ret and concert.collection \
                    and (collection_ids is False or str(concert.collection.collectionid) in rcollections) \
                    and concert.collection.permission in permission:
                ret.append(concert)
        ret = sorted(ret, key=lambda c: c.year if c.year else 0)
        return ret

    def performances(self, raagas=[], taalas=[]):
        ReleaseClass = self.get_object_map("release")
        IPClass = self.get_object_map("performance")
        concerts = ReleaseClass.objects.filter(recordings__instrumentperformance__artist=self)
        if raagas:
            concerts = concerts.filter(recordings__works__raaga__in=raagas)
        if taalas:
            concerts = concerts.filter(recordings__works__taala__in=taalas)
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

    def performs_percussion(self):
        """Returns True if the artist's main instrument is
           a percussion instrument"""
        return self.main_instrument and self.main_instrument.percussion

    def performs_lead(self):
        """Returns True if the artist's main instrument is
           a lead instrument (Vocals or Violin)"""

        VIOLIN = "089f123c-0f7d-4105-a64e-49de81ca8fa4"
        VOICE = "d92884b7-ee0c-46d5-96f3-918196ba8c5b"
        return self.main_instrument and str(self.main_instrument.mbid) in [VIOLIN, VOICE]

    def get_performed_taalas(self):
        taalamap = {}
        taalacount = collections.Counter()
        taalas = Taala.objects.filter(Q(work__recording__concert__artists=self) | Q(work__recording__instrumentperformance__artist=self))
        for t in taalas:
            taalacount[t.name] += 1
            if t.name not in taalamap:
                taalamap[t.name] = t
        taalas = []
        for t, count in taalacount.most_common():
            taalas.append((taalamap[t], count))
        return taalas

    def get_performed_raagas(self):
        """ Get the raaga of recordings that this artist has performed.

        The raaga comes from the work of recordings. Consider If the Artist
        has a specific performance relation to a recording/work or if they
        are a lead artist of the concert that the recording/work appears on.

        Returns:
          an ordered list of (raaga, count), ordered by count desc
        """
        raagamap = {}
        raagacount = collections.Counter()
        raagas = Raaga.objects.filter(Q(work__recording__concert__artists=self) | Q(work__recording__instrumentperformance__artist=self))
        for r in raagas:
            raagacount[r.name] += 1
            if r.name not in raagamap:
                raagamap[r.name] = r
        raagas = []
        for r, count in raagacount.most_common():
            raagas.append((raagamap[r], count))
        return raagas


class ArtistAlias(CarnaticStyle, data.models.ArtistAlias):
    pass


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


class Raaga(data.models.BaseModel, data.models.ImageMixin):
    missing_image = "raaga.jpg"

    name = models.CharField(max_length=50)
    common_name = models.CharField(max_length=50)
    uuid = models.UUIDField(db_index=True)
    image = models.ForeignKey(data.models.Image, blank=True, null=True, related_name="%(app_label)s_%(class)s_image")

    objects = managers.CarnaticRaagaManager()
    fuzzymanager = managers.FuzzySearchManager()

    def __unicode__(self):
        return self.name

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
        artists = Artist.objects.filter(primary_concerts__recordings__works__raaga=self).filter(main_instrument__in=[1, 2])
        for a in artists:
            artistcounter[a.pk] += 1
            if a.pk not in artistmap:
                artistmap[a.pk] = a
        artists = []
        for aid, count in artistcounter.most_common():
            artists.append(artistmap[aid])
        return artists

    def recordings(self, limit=None):
        recordings = Recording.objects.filter(works__raaga=self)
        if recordings is not None:
            recordings = recordings[:limit]
        return recordings

    def recordings_form(self, form=None):
        ret = Recording.objects.filter(Q(works__raaga=self) | Q(raagas=self))
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


class Taala(data.models.BaseModel, data.models.ImageMixin):
    missing_image = "taala.jpg"

    name = models.CharField(max_length=50)
    common_name = models.CharField(max_length=50)
    num_aksharas = models.IntegerField(null=True)
    uuid = models.UUIDField(db_index=True)
    image = models.ForeignKey(data.models.Image, blank=True, null=True, related_name="%(app_label)s_%(class)s_image")

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

    def works(self):
        return self.work_set.distinct().all()

    def composers(self):
        return Composer.objects.filter(works__taala=self).distinct()

    def artists(self):
        return Artist.objects.filter(primary_concerts__recordings__works__taala=self).distinct()

    def percussion_artists(self):
        artistmap = {}
        artistcounter = collections.Counter()
        artists = Artist.objects.filter(Q(instrumentperformance__recording__works__taala=self) & Q(instrumentperformance__instrument__percussion=True))
        for a in artists:
            artistcounter[a.pk] += 1
            if a.pk not in artistmap:
                artistmap[a.pk] = a
        artists = []
        for aid, count in artistcounter.most_common():
            artists.append(artistmap[aid])
        return artists

    def recordings(self, limit=None):
        recordings = Recording.objects.filter(works__taala=self)
        if recordings is not None:
            recordings = recordings[:limit]
        return recordings

    def recordings_form(self, form=None):
        ret = self.recording_set
        if form:
            ret = ret.filter(forms__name=form)
        return ret.all()


class Work(CarnaticStyle, data.models.Work):

    # (raaga, taala)
    raaga = models.ForeignKey('Raaga', blank=True, null=True)
    taala = models.ForeignKey('Taala', blank=True, null=True)
    form = models.ForeignKey('Form', blank=True, null=True)

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
    works = models.ManyToManyField('Work', through='RecordingWork')
    forms = models.ManyToManyField('Form', through='RecordingForm')

    raagas = models.ManyToManyField('Raaga', through='RecordingRaaga')
    taalas = models.ManyToManyField('Taala', through='RecordingTaala')

    objects = managers.CollectionRecordingManager()

    def get_raaga(self):
        forms = self.forms.all()
        if len(forms) == 0:
            # If we have no forms, return any locally saved raagas
            return self.raagas.all()

        if forms[0].attrfromrecording:
            return self.raagas.all()

        if len(self.works.all()):
            ret = []
            for w in self.works.all():
                if w.raaga:
                    ret.append(w.raaga)
            if ret:
                return ret

        # If we have no works (and we should), or we have works
        # and there are no attributes, just return from the
        # recording anyway (perhaps we got data from tags)
        return self.raagas.all()

    def get_taala(self):
        forms = self.forms.all()
        if len(forms) == 0:
            return self.taalas.all()

        if forms[0].attrfromrecording:
            return self.taalas.all()

        if len(self.works.all()):
            ret = []
            for w in self.works.all():
                if w.taala:
                    ret.append(w.taala)
            if ret:
                return ret
        # If we have no works (and we should), or we have works
        # and there are no attributes, just return from the
        # recording anyway (perhaps we got data from tags)
        return self.taalas.all()

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

    def get_dict(self):
        concert = Concert.objects.filter(recordings=self).first()
        title = None
        if concert:
            title = concert.title
        image = None
        if concert and concert.image:
            image = concert.image.image.url
        if not image:
            image = "/media/images/noconcert.jpg"
        artists = Artist.objects.filter(primary_concerts__recordings=self).values_list('name').all()
        return {
                "concert": title,
                "mainArtists": [item for sublist in artists for item in sublist],
                "name": self.title,
                "image": image,
                "linkToRecording": reverse("carnatic-recording", args=[self.mbid]),
                "collaborators": [],
                "selectedArtists": ""
        }


class InstrumentAlias(CarnaticStyle, data.models.InstrumentAlias):
    fuzzymanager = managers.FuzzySearchManager()
    objects = models.Manager()


class Instrument(CarnaticStyle, data.models.Instrument):
    fuzzymanager = managers.FuzzySearchManager()
    objects = managers.CarnaticInstrumentManager()

    def ordered_performers(self):
        artists, counts = self.performers()
        artists = sorted(artists, key=lambda a: counts[a], reverse=True)
        return artists

    def performers(self):
        artists = Artist.objects.filter(
                instrumentperformance__instrument=self).annotate(
                num_times=Count('instrumentperformance__instrument'))

        artistcount = {}
        ret = []
        for a in artists:
            ret.append(a)
            artistcount[a] = a.num_times

        return ret, artistcount

    def samples(self, limit=2):
        IPClass = self.get_object_map("performance")
        performances = list(IPClass.objects.filter(instrument=self).all())
        random.shuffle(performances)
        perf = performances[:limit]
        return [p.recording for p in perf]


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
