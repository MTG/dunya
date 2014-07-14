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
from django.conf import settings
from django.db.models import Q
from django.utils.text import slugify

import docserver

import os
import time
import math

class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

class SourceName(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

class Source(models.Model):
    # The source type that we got this data from (wikipedia, musicbrainz, etc)
    source_name = models.ForeignKey(SourceName)
    # The title of the page on the source website
    title = models.CharField(max_length=255)
    # The URL of the source
    uri = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"From %s: %s (%s)" % (self.source_name, self.uri, self.last_updated)

class Description(models.Model):
    """ A short description of a thing in the database.
    It could be a biography, or a description """
    source = models.ForeignKey(Source, blank=True, null=True)
    description = models.TextField()

    def __unicode__(self):
        return u"%s - %s" % (self.source, self.description[:100])

class Image(models.Model):
    """ An image of a thing in the database """
    source = models.ForeignKey(Source, blank=True, null=True)
    image = models.ImageField(upload_to="images")
    small_image = models.ImageField(upload_to="images", blank=True, null=True)

    def __unicode__(self):
        ret = u"%s" % (self.image.name, )
        if self.source:
            ret = u"%s from %s" % (ret, self.source.uri)
        return ret

class BaseModel(models.Model):
    class Meta:
        abstract = True

    source = models.ForeignKey(Source, blank=True, null=True, related_name="%(app_label)s_%(class)s_source_set")
    references = models.ManyToManyField(Source, blank=True, null=True, related_name="%(app_label)s_%(class)s_reference_set")
    description = models.ForeignKey(Description, blank=True, null=True, related_name="+")
    images = models.ManyToManyField(Image, related_name="%(app_label)s_%(class)s_image_set")

    def ref(self):
        u = {"url": self.source.uri, "title": self.source.source_name.name}
        return u

    def has_image(self):
        return bool(self.images.count())

    def get_image_url(self):
        media = settings.MEDIA_URL
        if self.images.all():
            image = self.images.all()[0]
            return os.path.join(media, image.image.name)
        else:
            if not hasattr(self, "missing_image"):
                missing_image = "artist.jpg"
            else:
                missing_image = self.missing_image
            return os.path.join(media, "missing", missing_image)

    def get_small_image_url(self):
        media = settings.MEDIA_URL
        if self.images.all():
            image = self.images.all()[0]
            if image.small_image:
                return os.path.join(media, image.small_image.name)
            else:
                return os.path.join(media, image.image.name)
        else:
            if not hasattr(self, "missing_image"):
                missing_image = "artist.jpg"
            else:
                missing_image = self.missing_image
            return os.path.join(media, "missing", missing_image)

    def get_style(self):
        raise Exception("need style")

    def get_object_map(self, key):
        raise Exception("need map")

class Artist(BaseModel):
    missing_image = "artist.jpg"

    class Meta:
        abstract = True

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female')
    )
    TYPE_CHOICES = (
        ('P', 'Person'),
        #('C', 'Composer'),
        ('G', 'Group')
    )
    name = models.CharField(max_length=200)
    mbid = UUIDField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    begin = models.CharField(max_length=10, blank=True, null=True)
    end = models.CharField(max_length=10, blank=True, null=True)
    artist_type = models.CharField(max_length=1, choices=TYPE_CHOICES, default='P')
    main_instrument = models.ForeignKey('Instrument', blank=True, null=True)
    group_members = models.ManyToManyField('Artist', blank=True, null=True, related_name='groups')
    dummy = models.BooleanField(default=False, db_index=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        viewname = "%s-artist" % (self.get_style(), )
        return reverse(viewname, args=[self.mbid, slugify(self.name)])

    def get_musicbrainz_url(self):
        return "http://musicbrainz.org/artist/%s" % self.mbid

    def concerts(self):
        ReleaseClass = self.get_object_map("release")
        concerts = ReleaseClass.objects.filter(Q(tracks__instrumentperformance__performer=self)|Q(instrumentconcertperformance__performer=self))
        return concerts.all()

    def recordings(self):
        IPClass = self.get_object_map("performance")
        performances = IPClass.objects.filter(performer=self)
        performance_recs = [p.recording for p in performances]

        # Releases where we were primary artist
        RelClass = self.get_object_map("release")
        pa_rels = RelClass.objects.filter(artists=self)
        # Releases where we were a relationship
        IRPClass = self.get_object_map("releaseperformance")
        rel_perfs = IRPClass.objects.filter(performer=self)
        rel_rels = [r.concert for r in rel_perfs]
        concerts = set(pa_rels) | set(rel_rels)
        concert_recordings = []
        for c in concerts:
            concert_recordings.extend(c.tracks.all())

        return list(set(performance_recs)|set(concert_recordings))

    def performances(self, raagas=[], taalas=[]):
        ReleaseClass = self.get_object_map("release")
        IPClass = self.get_object_map("performance")
        concerts = ReleaseClass.objects.filter(Q(tracks__instrumentperformance__performer=self)|Q(instrumentconcertperformance__performer=self))
        if raagas:
            concerts = concerts.filter(tracks__work__raaga__in=raagas)
        if taalas:
            concerts = concerts.filter(tracks__work__taala__in=taalas)
        concerts = concerts.distinct()
        ret = []
        for c in concerts:
            # If the relation is on the track, we'll have lots of performances,
            # restrict the list to just one instance
            # TODO: If more than one person plays the same instrument this won't work well
            performances = IPClass.objects.filter(performer=self, recording__concert=c).distinct()
            # Unique the instrument list
            instruments = []
            theperf = []
            for p in performances:
                if p.instrument not in instruments:
                    theperf.append(p)
                    instruments.append(p.instrument)
            ret.append((c, theperf))
        return ret

    def instruments(self):
        insts = []
        for perf in self.instrumentperformance_set.all():
            if perf.instrument.name not in insts:
                insts.append(perf.instrument)
        if insts:
            return insts[0]
        else:
            return None


class ArtistAlias(models.Model):
    class Meta:
        abstract = True
    artist = models.ForeignKey("Artist", related_name="aliases")
    alias = models.CharField(max_length=100)
    primary = models.BooleanField(default=False)
    locale = models.CharField(max_length=10, blank=True, null=True)

    def __unicode__(self):
        return u"%s (alias for %s)" % (self.alias, self.artist)

class Release(BaseModel):
    missing_image = "concert.jpg"

    class Meta:
        abstract = True
    mbid = UUIDField(blank=True, null=True)
    title = models.CharField(max_length=100)
    # Main artists on the concert
    artists = models.ManyToManyField('Artist', related_name='primary_concerts')
    artistcredit = models.CharField(max_length=255)
    year = models.IntegerField(blank=True, null=True)

    # These fields are specified on the concrete model classes because they might use
    # different spellings (Release/Concert)
    # Other artists who played on this concert (musicbrainz relationships)
    #performance = models.ManyToManyField('Artist', through="InstrumentReleasePerformance", related_name='accompanying_concerts')
    # Ordered tracks
    #tracks = models.ManyToManyField('Recording', through="ReleaseRecording")

    def length(self):
        tot_len = 0
        for t in self.tracks.all():
            tot_len += t.length/1000
        return time.strftime('%H:%M:%S', time.gmtime(tot_len))

    def __unicode__(self):
        ret = u", ".join([unicode(a) for a in self.artists.all()])
        return u"%s (%s)" % (self.title, ret)

    def get_absolute_url(self):
        viewname = "%s-release" % (self.get_style(), )
        return reverse(viewname, args=[self.mbid, slugify(self.title)])

    def get_musicbrainz_url(self):
        return "http://musicbrainz.org/release/%s" % self.mbid

    def artistnames(self):
        return self.artists.all()

    def tracklist(self):
        """Return an ordered list of recordings in this concert"""
        tracks = self.get_object_map("recording").objects.filter(
                concertrecording__concert=self).order_by('concertrecording__track')
        return tracks

    def performers(self):
        """ The performers on a concert are those who are in the performance relations,
        both on the concert and the concerts recordings.
        TODO: Should this return a performance object, or an artist?
        """
        person = set()
        ret = []
        IPClass = self.get_object_map("performance")
        ICPClass = self.get_object_map("releaseperformance")
        IClass = self.get_object_map("instrument")
        for p in self.performance.all():
            if p.id not in person:
                person.add(p.id)
                perf = ICPClass.objects.get(concert=self, performer=p)
                ret.append(perf)
        for t in self.tracks.all():
            for p in t.performance.all():
                if p.id not in person:
                    perf = IPClass.objects.get(recording=t, performer=p)
                    person.add(p.id)
                    ret.append(perf)
        if len(self.artists.all()):
            maina = self.artists.all()[0]
            if maina.id not in person:
                dummyp = ICPClass()
                dummyp.performer = maina
                dummyp.concert = self
                if maina.main_instrument:
                    dummyp.instrument = maina.main_instrument
                else:
                    # TODO: If we don't know the instrument it's almost certainly a vocalist
                    dummyp.instrument = IClass.objects.get(pk=1)
                ret.insert(0, dummyp)
        return ret

class Work(BaseModel):
    class Meta:
        abstract = True
    title = models.CharField(max_length=100)
    mbid = UUIDField(blank=True, null=True)
    composers = models.ManyToManyField('Composer', blank=True, null=True, related_name="works")
    lyricists = models.ManyToManyField('Composer', blank=True, null=True, related_name="lyric_works")

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        viewname = "%s-work" % (self.get_style(), )
        return reverse(viewname, args=[self.mbid, slugify(self.title)])

    def get_musicbrainz_url(self):
        return "http://musicbrainz.org/work/%s" % self.mbid

    def concerts(self):
        ReleaseClass = self.get_object_map("concert")
        return ReleaseClass.objects.filter(tracks__work=self).all()

    def artists(self):
        ArtistClass = self.get_object_map("artist")
        return ArtistClass.objects.filter(primary_concerts__tracks__work=self).distinct()

class Recording(BaseModel):
    class Meta:
        abstract = True
    title = models.CharField(max_length=200)
    mbid = UUIDField(blank=True, null=True)
    length = models.IntegerField(blank=True, null=True)
    performance = models.ManyToManyField('Artist', through="InstrumentPerformance")

    # On concrete class because a recording may have >1 work in some styles
    #work = models.ForeignKey('Work', blank=True, null=True)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        viewname = "%s-recording" % (self.get_style(), )
        return reverse(viewname, args=[self.mbid, slugify(self.title)])

    def get_musicbrainz_url(self):
        return "http://musicbrainz.org/recording/%s" % self.mbid

    def absolute_mp3_url(self):
        try:
            url = docserver.util.docserver_get_mp3_url(self.mbid)
        except docserver.util.NoFileException:
            url = None
        return url

    def length_format(self):
        numsecs = self.length/1000
        minutes = math.floor(numsecs / 60.0)
        hours = math.floor(minutes / 60.0)
        minutes = math.floor(minutes - hours*60)
        seconds = math.floor(numsecs - hours*3600 - minutes*60)
        if hours:
            val = "%02d:%02d:%02d" % (hours, minutes, seconds)
        else:
            val = "%02d:%02d" % (minutes, seconds)

        return val

    def length_seconds(self):
        return self.length / 1000

    def all_artists(self):
        ArtistClass = self.get_object_map("artist")
        primary_artists = ArtistClass.objects.filter(primary_concerts__tracks=self)

        IPClass = self.get_object_map("performance")
        recperfs = IPClass.objects.filter(recording=self)
        rec_artists = [r.performer for r in recperfs]

        all_as = set(primary_artists) | set(rec_artists)
        return list(all_as)

    def waveform_image(self):
        # TODO: Select this image in a better way, or show a better
        # representation
        try:
            # we return "4", because it might be more interesting than 1, but if it fails
            # (e.g. only 3?) then just return 1
            return docserver.util.docserver_get_url(self.mbid, "audioimages", "waveform32", 4)
        except docserver.util.NoFileException:
            try:
                return docserver.util.docserver_get_url(self.mbid, "audioimages", "waveform32", 1)
            except docserver.util.NoFileException:
                return ""


class InstrumentAlias(models.Model):
    class Meta:
        abstract = True
    name = models.CharField(max_length=50)
    instrument = models.ForeignKey("Instrument", related_name="aliases")

    def __unicode__(self):
        return self.name

class Instrument(BaseModel):
    class Meta:
        abstract = True
    missing_image = "instrument.jpg"

    percussion = models.BooleanField(default=False)
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        viewname = "%s-instrument" % (self.get_style(), )
        return reverse(viewname, args=[str(self.id), slugify(self.name)])

    def artists(self):
        ArtistClass = self.get_object_map("artist")
        return ArtistClass.objects.filter(instrumentperformance__instrument=self).distinct().all()

class InstrumentPerformance(models.Model):
    class Meta:
        abstract = True
    recording = models.ForeignKey('Recording')
    performer = models.ForeignKey('Artist')
    instrument = models.ForeignKey('Instrument')
    lead = models.BooleanField(default=False)

    def __unicode__(self):
        return u"%s playing %s on %s" % (self.performer, self.instrument, self.recording)

class Composer(BaseModel):
    missing_image = "artist.jpg"

    class Meta:
        abstract = True
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female')
    )
    name = models.CharField(max_length=200)
    mbid = UUIDField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    begin = models.CharField(max_length=10, blank=True, null=True)
    end = models.CharField(max_length=10, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def get_musicbrainz_url(self):
        return "http://musicbrainz.org/composer/%s" % self.mbid

    def get_absolute_url(self):
        viewname = "%s-composer" % (self.get_style(), )
        return reverse(viewname, args=[self.mbid, slugify(self.name)])

class ComposerAlias(models.Model):
    class Meta:
        abstract = True
    composer = models.ForeignKey("Composer", related_name="aliases")
    alias = models.CharField(max_length=100)
    primary = models.BooleanField(default=False)
    locale = models.CharField(max_length=10, blank=True, null=True)

    def __unicode__(self):
        return u"%s (alias for %s)" % (self.alias, self.composer)

class VisitLog(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=100, blank=True, null=True)
    # ipv4 only!
    ip = models.CharField(max_length=16)
    path = models.CharField(max_length=256)

    def __unicode__(self):
        return u"%s: (%s/%s): %s" % (self.date, self.user, self.ip, self.path)

