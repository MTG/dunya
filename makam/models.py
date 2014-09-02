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

import collections

import data.models

class MakamStyle(object):
    def get_style(self):
        return "makam"

    def get_object_map(self, key):
        return {"performance": InstrumentPerformance,
                "release": Release,
                "composer": Composer,
                "artist": Artist,
                "recording": Recording,
                "work": Work,
                "instrument": Instrument
                }[key]

class ArtistAlias(MakamStyle, data.models.ArtistAlias):
    pass

class Artist(MakamStyle, data.models.Artist):

    def collaborating_artists(self):
        our_releases = Release.objects.filter(Q(recordings__instrumentperformance__artist=self)|Q(artists=self)).distinct()
        others = Artist.objects.filter(Q(instrumentperformance__recording__release__in=our_releases)|Q(primary_concerts__in=our_releases)).exclude(pk=self.pk).distinct()
        counts = collections.Counter(others)
        return [a for a, c in counts.most_common(10)]

    def main_releases(self):
        """ Releases where this artist is named on the cover """
        return self.primary_concerts.all()

    def accompanying_releases(self):
        """ Releases where this artist performs, but isn't named on the cover """
        return Release.objects.filter(recordings__instrumentperformance__artist=self).exclude(id__in=self.primary_concerts.all()).distinct()

class ComposerAlias(MakamStyle, data.models.ComposerAlias):
    pass

class Composer(MakamStyle, data.models.Composer):
    pass

class Release(MakamStyle, data.models.Release):
    is_concert = models.BooleanField(default=False)
    recordings = models.ManyToManyField('Recording', through="ReleaseRecording")

    def tracklist(self):
        """Return an ordered list of recordings in this release"""
        return self.recordings.order_by('releaserecording')

    def instruments_for_artist(self, artist):
        """ Returns a list of instruments that this
        artist performs on this release."""
        return Instrument.objects.filter(instrumentperformance__artist=artist).distinct()

    def performers(self):
        """ The performers on a release are those who are in the performance
        relations, and the lead artist of the release (if not in relations)
        """
        artists = self.artists.all()
        performers = Artist.objects.filter(instrumentperformance__recording__release=self).exclude(id__in=artists).distinct()
        return list(artists) + list(performers)

class ReleaseRecording(models.Model):
    release = models.ForeignKey('Release')
    recording = models.ForeignKey('Recording')
    # The number that the track comes in the release. Numerical 1-n
    track = models.IntegerField()

    class Meta:
        ordering = ("track", )

    def __unicode__(self):
        return u"%s: %s from %s" % (self.track, self.recording, self.release)

class RecordingWork(models.Model):
    work = models.ForeignKey("Work")
    recording = models.ForeignKey("Recording")
    sequence = models.IntegerField()

    class Meta:
        ordering = ("sequence", )

    def __unicode__(self):
        return u"%s: %s" % (self.sequence, self.work.title)

class Recording(MakamStyle, data.models.Recording):
    works = models.ManyToManyField("Work", through="RecordingWork")

    # the form Taksim refers to an instrumental improvisation
    has_taksim = models.BooleanField(default=False)
    # and form gazel is a vocal improvisation
    has_gazel = models.BooleanField(default=False)
    # If either of these flags is set, we don't have a work to store
    # the `makam` field to, so we store it here. Only use this field
    # if one of the above two flags are set.
    makam = models.ManyToManyField("Makam", blank=True, null=True)

    def releaselist(self):
        return self.release_set.all()

    def worklist(self):
        return self.works.order_by('recordingwork')

    def instruments_for_artist(self, artist):
        """ Returns a list of instruments that this
        artist performs on this release."""
        return Instrument.objects.filter(instrumentperformance__artist=artist, instrumentperformance__recording=self).distinct()

    def performers(self):
        """ The performers on a recording are those who are in the performance
        relations, and the lead artist of the recording's release (if not in relations)
        """
        artists = Artist.objects.filter(primary_concerts__recordings=self).distinct()
        performers = Artist.objects.filter(instrumentperformance__recording=self).exclude(id__in=artists).distinct()
        return list(artists) + list(performers)

class InstrumentPerformance(MakamStyle, data.models.InstrumentPerformance):
    pass

class Instrument(MakamStyle, data.models.Instrument):
    pass

class UnaccentManager(models.Manager):
    """ A manager to use postgres' unaccent module to get items
    with a specified `name` field """
    def unaccent_get(self, name):
        return super(UnaccentManager, self).get_queryset().extra(where=["unaccent(lower(name)) = unaccent(lower(%s))"], params=[name]).get()

class MakamAlias(models.Model):
    name = models.CharField(max_length=100)
    makam = models.ForeignKey("Makam", related_name="aliases")

    objects = UnaccentManager()

    def __unicode__(self):
        return self.name

class Makam(models.Model):
    name = models.CharField(max_length=100)

    objects = UnaccentManager()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('makam-makam', args=[str(self.id)])

class UsulAlias(models.Model):
    name = models.CharField(max_length=100)
    usul = models.ForeignKey("Usul", related_name="aliases")

    objects = UnaccentManager()

    def __unicode__(self):
        return self.name

class Usul(models.Model):
    name = models.CharField(max_length=100)

    objects = UnaccentManager()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('makam-usul', args=[str(self.id)])

class FormAlias(models.Model):
    name = models.CharField(max_length=100)
    form = models.ForeignKey("Form", related_name="aliases")

    objects = UnaccentManager()

    def __unicode__(self):
        return self.name

class Form(models.Model):
    name = models.CharField(max_length=100)

    objects = UnaccentManager()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('makam-form', args=[str(self.id)])

class Work(MakamStyle, data.models.Work):
    composition_date = models.CharField(max_length=100, blank=True, null=True)

    makam = models.ManyToManyField(Makam, blank=True, null=True)
    usul = models.ManyToManyField(Usul, blank=True, null=True)
    form = models.ManyToManyField(Form, blank=True, null=True)
