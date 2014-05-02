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

from hindustani import managers
import data.models

class HindustaniStyle(object):
    def get_style(self):
        return "hindustani"
    def get_object_map(self, key):
        return {"performance": InstrumentPerformance,
                "release": Release,
                "composer": Composer,
                "artist": Artist,
                "recording": Recording,
                "work": Work,
                "instrument": Instrument
                }[key]

class Instrument(HindustaniStyle, data.models.Instrument):
    objects = managers.HindustaniInstrumentManager()

    def performers(self):
        artistcount = collections.Counter()
        for p in InstrumentPerformance.objects.filter(instrument=self):
            artistcount[p.performer] += 1

        return [i[0] for i in artistcount.most_common()]

    @classmethod
    def get_filter_criteria(cls):
        ret = {"url": reverse('hindustani-instrument-search'),
               "name": "Instrument",
               "data": []
              }
        return ret

class Artist(HindustaniStyle, data.models.Artist):
    def releases(self):
        # Releases in which we were the primary artist
        ret = []
        ret.extend([r for r in self.primary_concerts.all()])
        # Releases in which we performed
        ret.extend([r for r in Release.objects.filter(tracks__instrumentperformance__performer=self).distinct()])
        return ret

    def collaborating_artists(self):
        # Get all concerts
        # For each artist on the concerts (both types), add a counter
        # top 10 artist ids + the concerts they collaborate on
        c = collections.Counter()
        releases = collections.defaultdict(set)
        for release in self.releases():
            for p in release.performers():
                thea = p.performer
                if thea.id != self.id:
                    releases[thea.id].add(release)
                    c[thea.id] += 1

        return [(Artist.objects.get(pk=pk), list(releases[pk])) for pk,count in c.most_common()]

    @classmethod
    def get_filter_criteria(cls):
        ret = {"url": reverse('hindustani-artist-search'),
               "name": "Artist",
               "data": []
              }
        return ret

class ArtistAlias(HindustaniStyle, data.models.ArtistAlias):
    pass

class ReleaseRecording(models.Model):
    """ Links a release to a recording with an implicit ordering """
    release = models.ForeignKey('Release')
    recording = models.ForeignKey('Recording')
    # The number that the track comes in the concert. Numerical 1-n
    track = models.IntegerField()

    def __unicode__(self):
        return u"%s: %s from %s" % (self.track, self.recording, self.release)

class Release(HindustaniStyle, data.models.Release):
    tracks = models.ManyToManyField("Recording", through="ReleaseRecording")

    def performers(self):
        artists = set()
        performances = []
        for ip in InstrumentPerformance.objects.filter(recording__release=self):
            if ip.performer not in artists:
                artists.add(ip.performer)
                performances.append(ip)
        return performances

    @classmethod
    def get_filter_criteria(cls):
        ret = {"url": reverse('hindustani-release-search'),
               "name": "Release",
               "data": []
              }
        return ret


class RecordingRaag(models.Model):
    recording = models.ForeignKey("Recording")
    raag = models.ForeignKey("Raag")
    sequence = models.IntegerField()

class RecordingTaal(models.Model):
    recording = models.ForeignKey("Recording")
    taal = models.ForeignKey("Taal")
    sequence = models.IntegerField()

class RecordingLaya(models.Model):
    recording = models.ForeignKey("Recording")
    laya = models.ForeignKey("Laya")
    sequence = models.IntegerField()

class RecordingSection(models.Model):
    recording = models.ForeignKey("Recording")
    section = models.ForeignKey("Section")
    sequence = models.IntegerField()

class RecordingForm(models.Model):
    recording = models.ForeignKey("Recording")
    form = models.ForeignKey("Form")
    sequence = models.IntegerField()

class Recording(HindustaniStyle, data.models.Recording):

    raags = models.ManyToManyField("Raag", through="RecordingRaag")
    taals = models.ManyToManyField("Taal", through="RecordingTaal")
    layas = models.ManyToManyField("Laya", through="RecordingLaya")
    sections = models.ManyToManyField("Section", through="RecordingSection")
    forms = models.ManyToManyField("Form", through="RecordingForm")
    works = models.ManyToManyField("Work", through="WorkTime")

class InstrumentPerformance(HindustaniStyle, data.models.InstrumentPerformance):
    pass

class Composer(HindustaniStyle, data.models.Composer):
    pass

class ComposerAlias(HindustaniStyle, data.models.ComposerAlias):
    pass

class Lyrics(models.Model):
    lyrics = models.CharField(max_length=50)

class Work(HindustaniStyle, data.models.Work):
    lyrics = models.ForeignKey("Lyrics", blank=True, null=True)

class WorkTime(models.Model):
    # The time in a recording that a work occurs (recordings can consist of
    # many works)
    recording = models.ForeignKey(Recording)
    work = models.ForeignKey(Work)
    # a worktime is always ordered ...
    sequence = models.IntegerField()
    # but its time is optional (we may not have it yet)
    time = models.IntegerField(blank=True, null=True)

class Section(models.Model):
    name = models.CharField(max_length=50)
    common_name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name.capitalize()

class SectionAlias(models.Model):
    name = models.CharField(max_length=50)
    section = models.ForeignKey("Section", related_name="aliases")

    def __unicode__(self):
        return self.name

class Raag(models.Model):
    missing_image = "raag.jpg"

    objects = managers.HindustaniRaagManager()

    name = models.CharField(max_length=50)
    common_name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name.capitalize()

    def get_absolute_url(self):
        return reverse('hindustani-raag', args=[str(self.id)])

    def works(self):
        return Work.objects.filter(recording__raags=self).distinct()

    def composers(self):
        return Composer.objects.filter(works__recording__raags=self).distinct()

    def artists(self):
        artistmap = {}
        artistcounter = collections.Counter()
        voice = Instrument.objects.fuzzy("voice")
        artists = Artist.objects.filter(primary_concerts__tracks__raags=self)
        for a in artists:
            artistcounter[a.pk] += 1
            if a.pk not in artistmap:
                artistmap[a.pk] = a
        artists = []
        for aid, count in artistcounter.most_common():
            artists.append(artistmap[aid])
        return artists

    @classmethod
    def get_filter_criteria(cls):
        ret = {"url": reverse('hindustani-raag-search'),
               "name": "Raag",
               "data": []
              }
        return ret

class RaagAlias(models.Model):
    name = models.CharField(max_length=50)
    raag = models.ForeignKey("Raag", related_name="aliases")

    def __unicode__(self):
        return self.name

class Taal(data.models.BaseModel):
    missing_image = "taal.jpg"

    objects = managers.HindustaniTaalManager()

    name = models.CharField(max_length=50)
    common_name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name.capitalize()

    def get_absolute_url(self):
        return reverse('hindustani-taal', args=[str(self.id)])

    def percussion_artists(self):
        artistmap = {}
        artistcounter = collections.Counter()
        artists = Artist.objects.filter(Q(instrumentperformance__recording__taals=self) & Q(instrumentperformance__instrument__percussion=True))
        for a in artists:
            artistcounter[a.pk] += 1
            if a.pk not in artistmap:
                artistmap[a.pk] = a
        artists = []
        for aid, count in artistcounter.most_common():
            artists.append(artistmap[aid])
        return artists

    def works(self):
        return Work.objects.filter(recording__taals=self).distinct()

    def composers(self):
        return Composer.objects.filter(works__recording__taals=self).distinct()

    @classmethod
    def get_filter_criteria(cls):
        ret = {"url": reverse('hindustani-taal-search'),
               "name": "Taal",
               "data": []
              }
        return ret

class TaalAlias(models.Model):
    name = models.CharField(max_length=50)
    taal = models.ForeignKey("Taal", related_name="aliases")

    def __unicode__(self):
        return self.name

class Laya(models.Model):
    missing_image = "laya.jpg"

    objects = managers.HindustaniLayaManager()

    name = models.CharField(max_length=50)
    common_name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name.capitalize()

    def get_absolute_url(self):
        return reverse('hindustani-laya', args=[str(self.id)])

    @classmethod
    def get_filter_criteria(cls):
        ret = {"url": reverse('hindustani-laya-search'),
               "name": "Laya",
               "data": []
              }
        return ret

class LayaAlias(models.Model):
    name = models.CharField(max_length=50)
    laya = models.ForeignKey("Laya", related_name="aliases")

    def __unicode__(self):
        return self.name

class Form(models.Model):
    missing_image = "form.jpg"

    objects = managers.HindustaniFormManager()

    name = models.CharField(max_length=50)
    common_name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name.capitalize()

    def get_absolute_url(self):
        return reverse('hindustani-form', args=[str(self.id)])

    def recordings(self):
        return self.recording_set.all()

    @classmethod
    def get_filter_criteria(cls):
        ret = {"url": reverse('hindustani-form-search'),
               "name": "form",
               "data": []
              }
        return ret

class FormAlias(models.Model):
    name = models.CharField(max_length=50)
    form = models.ForeignKey("Form", related_name="aliases")

    def __unicode__(self):
        return self.name
