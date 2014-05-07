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

    # Some instruments exist because they have relationships, but we
    # don't want to show them
    hidden = models.BooleanField(default=False)

    def performers(self):
        artistcount = collections.Counter()
        for p in InstrumentPerformance.objects.filter(instrument=self):
            artistcount[p.performer] += 1

        return [a for a, _ in artistcount.most_common()]

    def related_items(self):
        ret = []
        # instrument
        ret.append( ("instrument", self) )
        # artists (first 5, ordered by number of performances)
        for p in self.performers()[:5]:
            ret.append( ("artist", p) )
        return ret

    @classmethod
    def get_filter_criteria(cls):
        ret = {"url": reverse('hindustani-instrument-search'),
               "name": "Instrument",
               "data": []
              }
        return ret

class Artist(HindustaniStyle, data.models.Artist):
    missing_image = "hindustaniartist.jpg"

    def related_items(self):
        ret = []
        # artist
        ret.append( ("artist", self) )
        # instrument
        if self.main_instrument:
            ret.append( ("instrument", self.main_instrument) )
        # raags
        forms = collections.Counter()
        raags = collections.Counter()
        for rel in self.releases():
            for tr in rel.tracks.all():
                for fo in tr.forms.all():
                    forms[fo] += 1
                for ra in tr.raags.all():
                    raags[ra] += 1

        for ra, _ in raags.most_common(5):
            ret.append( ("raag", ra) )

        # releases
        for rel in self.releases()[:5]:
            ret.append( ("release", rel) )
        # forms
        for fo, _ in forms.most_common(5):
            ret.append( ("form", fo) )

        return ret

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

    def related_items(self):
        ret = []
        # release
        ret.append( ("release", self) )
        # artist
        # instruments
        for p in self.performers()[:5]:
            ret.append( ("artist", p.performer) )
            ret.append( ("instrument", p.instrument) )
        # taals
        # raags
        # forms
        taals = collections.Counter()
        raags = collections.Counter()
        forms = collections.Counter()
        for tr in self.tracks.all():
            for ta in tr.taals.all():
                taals[ta] += 1
            for ra in tr.raags.all():
                raags[ra] += 1
            for fo in tr.forms.all():
                forms[fo] += 1
        for ta, _ in taals.most_common(5):
            ret.append( ("taal", ta) )
        for ra, _ in raags.most_common(5):
            ret.append( ("raag", ra) )
        for fo, _ in forms.most_common(5):
            ret.append( ("form", fo) )
        return ret

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

class Raag(data.models.BaseModel):
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
        artists = Artist.objects.filter(primary_concerts__tracks__raags=self)
        for a in artists:
            artistcounter[a.pk] += 1
            if a.pk not in artistmap:
                artistmap[a.pk] = a
        artists = []
        for aid, count in artistcounter.most_common():
            artists.append(artistmap[aid])
        return artists

    def related_items(self):
        # TODO: This should just be releases of the shown artists, maybe?
        ret = []
        # raag
        ret.append( ("raag", self) )
        # artist
        for a in self.artists()[:5]:
            ret.append( ("artist", a) )
        # releases
        releases = Release.objects.filter(tracks__in=self.recording_set.all())
        for r in releases:
            ret.append( ("release", r) )
        # forms (of recordings that also have this raag)
        forms = collections.Counter()
        for tr in self.recording_set.all():
            for fo in tr.forms.all():
                forms[fo] += 1
        for fo, _ in forms.most_common(5):
            ret.append( ("form", fo) )
        return ret

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

    def related_items(self):
        # TODO: This should just be releases of the shown artists, maybe?
        ret = []
        # taal
        ret.append( ("taal", self) )
        # artists
        for a in self.percussion_artists()[:5]:
            ret.append( ("artist", a) )

        # releases
        releases = Release.objects.filter(tracks__in=self.recording_set.all())
        for r in releases[:5]:
            ret.append( ("release", r) )
        # forms (of recordings that also have this taal)
        forms = collections.Counter()
        for tr in self.recording_set.all():
            for fo in tr.forms.all():
                forms[fo] += 1
        for fo, _ in forms.most_common(5):
            ret.append( ("form", fo) )
        return ret

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

class Laya(data.models.BaseModel):
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
    
    @data.models.ClassProperty
    @classmethod
    def Dhrut(cls):
        return cls.objects.fuzzy('dhrut')
    
    @data.models.ClassProperty
    @classmethod
    def Madhya(cls):
        return cls.objects.fuzzy('madhya')
    
    @data.models.ClassProperty
    @classmethod
    def Vilambit(cls):
        return cls.objects.fuzzy('vilambit')

class LayaAlias(models.Model):
    name = models.CharField(max_length=50)
    laya = models.ForeignKey("Laya", related_name="aliases")

    def __unicode__(self):
        return self.name

class Form(data.models.BaseModel):
    missing_image = "form.jpg"

    objects = managers.HindustaniFormManager()

    name = models.CharField(max_length=50)
    common_name = models.CharField(max_length=50)

    def artists(self):
        """ Artists who are the lead artist of a release and 
        who perform tracks with this form """
        artistmap = {}
        artistcounter = collections.Counter()
        artists = Artist.objects.filter(primary_concerts__tracks__forms=self)
        for a in artists:
            artistcounter[a.pk] += 1
            if a.pk not in artistmap:
                artistmap[a.pk] = a
        artists = []
        for aid, count in artistcounter.most_common():
            artists.append(artistmap[aid])
        return artists

    def __unicode__(self):
        return self.name.capitalize()

    def get_absolute_url(self):
        return reverse('hindustani-form', args=[str(self.id)])

    def recordings(self):
        return self.recording_set.all()

    def related_items(self):
        # TODO: Only raags that are in the releases shown
        # (or releases of the shown raags)
        ret = []
        # form
        ret.append( ("form", self) )
        # artists
        for a in self.artists()[:5]:
            ret.append( ("artist", a) )

        # raags (of recordings that also have this form)
        raags = collections.Counter()
        for tr in self.recording_set.all():
            for ra in tr.raags.all():
                raags[ra] += 1
        for ra, _ in raags.most_common(5):
            ret.append( ("raag", ra) )
        # releases
        releases = Release.objects.filter(tracks__in=self.recording_set.all())
        for r in releases[:5]:
            ret.append( ("release", r) )
        return ret

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
