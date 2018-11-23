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
from typing import List, Optional

from django.urls import reverse
from django.db import models
from django.db.models import Q
from django.utils.text import slugify

import data.models
from hindustani import managers


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
    class Meta:
        ordering = ['id']

    objects = managers.HindustaniInstrumentManager()

    def performers(self):
        artistcount = collections.Counter()
        for p in InstrumentPerformance.objects.filter(instrument=self):
            artistcount[p.artist] += 1

        return [a for a, _ in artistcount.most_common()]

    def related_items(self):
        ret = []
        # instrument
        ret.append(("instrument", self))
        # artists (first 5, ordered by number of performances)
        for p in self.performers()[:5]:
            ret.append(("artist", p))
        return ret


class Artist(HindustaniStyle, data.models.Artist):
    class Meta:
        ordering = ['id']

    missing_image = "hindustaniartist.jpg"

    def related_items(self):
        """ Just the related things. Artist / their instrument """
        ret = []
        # artist
        ret.append(("artist", self))
        # instrument
        if self.main_instrument:
            ret.append(("instrument", self.main_instrument))
        return ret

    def combined_related_items(self, artists=None, raags=None, taals=None, forms=None):
        ret = []

        # If `artists` is set, we want all releases that this artist has
        # performed in that all these other artists have too
        our_releases = self.releases()

        if artists:
            other_releases = []
            for a in artists:
                other_releases.extend(a.releases())
            releases = list(set(our_releases) & set(other_releases))
        else:
            releases = our_releases

        # If Raags, Taals, or Forms is set, limit the releases by these,
        # and then show all the selcted raags and forms

        if raags or taals or forms:
            new_releases = []
            if raags:
                for r in releases:
                    if r.recordings.filter(raags__in=raags).exists():
                        new_releases.append(r)
            if taals:
                for r in releases:
                    if r.recordings.filter(taals__in=taals).exists():
                        new_releases.append(r)
            if forms:
                for r in releases:
                    if r.recordings.filter(forms__in=forms).exists():
                        new_releases.append(r)
            releases = new_releases

        # Otherwise, show the most common raags and forms
        form_count = collections.Counter()
        raag_count = collections.Counter()
        for rel in releases:
            for tr in rel.recordings.all():
                for fo in tr.forms.all():
                    form_count[fo] += 1
                for ra in tr.raags.all():
                    raag_count[ra] += 1

        if raags:
            for r in raags:
                ret.append(("raag", r))
        else:
            for ra, _ in raag_count.most_common(5):
                if not raags or ra not in raags:
                    ret.append(("raag", ra))

        if taals:
            for t in taals:
                ret.append(("taal", t))

        # forms
        if forms:
            for f in forms:
                ret.append(("form", f))
        elif not raags and not taals:
            for fo, _ in form_count.most_common(5):
                if not forms or fo not in forms:
                    ret.append(("form", fo))

        # releases
        for rel in releases[:5]:
            ret.append(("release", rel))

        return ret

    def releases(self, collection_ids: Optional[List[str]]=None, permission=False):
        if collection_ids is None:
            collection_ids = []
        if not permission:
            permission = ["U"]

        # Releases in which we were the primary artist
        ret = []
        ret.extend([r for r in self.primary_concerts.with_permissions(collection_ids, permission).all()])

        # Releases of my groups
        for a in self.groups.all():
            for c in a.releases():
                if c not in ret and c.collection \
                        and (not collection_ids or str(c.collection.collectionid) in collection_ids) \
                        and c.collection.permission in permission:
                    ret.append(c)

        # Releases in which we performed
        ret.extend([r for r in Release.objects.with_permissions(collection_ids, permission).filter(
            recordings__instrumentperformance__artist=self).distinct()])
        ret = list(set(ret))
        ret = sorted(ret, key=lambda c: c.year if c.year else 0)
        return ret

    def collaborating_artists(self):
        # Get all concerts
        # For each artist on the concerts (both types), add a counter
        # top 10 artist ids + the concerts they collaborate on
        c = collections.Counter()
        releases = collections.defaultdict(set)
        for release in self.releases():
            for p in release.performers():
                if p != self:
                    releases[p].add(release)
                    c[p] += 1

        return [(artist, list(releases[artist])) for artist, count in c.most_common()]

    def recordings(self, collection_ids: Optional[List[str]]=None, permission=False):
        if collection_ids is None:
            collection_ids = []
        return Recording.objects.with_permissions(collection_ids, permission).filter(
            Q(instrumentperformance__artist=self) | Q(release__artists=self)).distinct()


class ArtistAlias(HindustaniStyle, data.models.ArtistAlias):
    pass


class ReleaseRecording(models.Model):
    """ Links a release to a recording with an implicit ordering """
    release = models.ForeignKey('Release', on_delete=models.CASCADE)
    recording = models.ForeignKey('Recording', on_delete=models.CASCADE)
    # The number that the track comes in the concert. Numerical 1-n
    track = models.IntegerField()
    # The disc number. 1-n
    disc = models.IntegerField()
    # The track number within this disc. 1-n
    disctrack = models.IntegerField()

    class Meta:
        ordering = ("track",)

    def __str__(self):
        return u"%s: %s from %s" % (self.track, self.recording, self.release)


class Release(HindustaniStyle, data.models.Release):
    class Meta:
        ordering = ['id']

    recordings = models.ManyToManyField("Recording", through="ReleaseRecording")
    collection = models.ForeignKey('data.Collection', blank=True, null=True, related_name="hindustani_releases", on_delete=models.CASCADE)

    objects = managers.HindustaniReleaseManager()

    def tracklist(self):
        """Return an ordered list of recordings in this release"""
        return self.recordings.order_by('releaserecording')

    def instruments_for_artist(self, artist):
        """ Returns a list of instruments that this
        artist performs on this release."""
        return Instrument.objects.filter(instrumentperformance__artist=artist).distinct()

    def performers(self):
        """ The performers on a release are those who are in the performance
        relations, and the lead artist of the release (listed first)
        """
        ret = self.artists.all()
        artists = Artist.objects.filter(instrumentperformance__recording__release=self).exclude(id__in=ret).distinct()
        return list(ret) + list(artists)

    def related_items(self):
        ret = []
        # release
        ret.append(("release", self))
        # artist
        # instruments
        for p in self.performers()[:5]:
            ret.append(("artist", p))
            if p.main_instrument:
                ret.append(("instrument", p.main_instrument))
        # taals
        # raags
        # forms
        taals = collections.Counter()
        raags = collections.Counter()
        forms = collections.Counter()
        for tr in self.recordings.all():
            for ta in tr.taals.all():
                taals[ta] += 1
            for ra in tr.raags.all():
                raags[ra] += 1
            for fo in tr.forms.all():
                forms[fo] += 1
        for ta, _ in taals.most_common(5):
            ret.append(("taal", ta))
        for ra, _ in raags.most_common(5):
            ret.append(("raag", ra))
        for fo, _ in forms.most_common(5):
            ret.append(("form", fo))
        return ret


class RecordingRaag(models.Model):
    recording = models.ForeignKey("Recording", on_delete=models.CASCADE)
    raag = models.ForeignKey("Raag", on_delete=models.CASCADE)
    sequence = models.IntegerField()


class RecordingTaal(models.Model):
    recording = models.ForeignKey("Recording", on_delete=models.CASCADE)
    taal = models.ForeignKey("Taal", on_delete=models.CASCADE)
    sequence = models.IntegerField()


class RecordingLaya(models.Model):
    recording = models.ForeignKey("Recording", on_delete=models.CASCADE)
    laya = models.ForeignKey("Laya", on_delete=models.CASCADE)
    sequence = models.IntegerField()


class RecordingForm(models.Model):
    recording = models.ForeignKey("Recording", on_delete=models.CASCADE)
    form = models.ForeignKey("Form", on_delete=models.CASCADE)
    sequence = models.IntegerField()


class Recording(HindustaniStyle, data.models.Recording):
    class Meta:
        ordering = ['id']

    raags = models.ManyToManyField("Raag", through="RecordingRaag")
    taals = models.ManyToManyField("Taal", through="RecordingTaal")
    layas = models.ManyToManyField("Laya", through="RecordingLaya")
    forms = models.ManyToManyField("Form", through="RecordingForm")
    works = models.ManyToManyField("Work", through="WorkTime")

    objects = managers.HindustaniRecordingManager()

    def get_dict(self):
        release = Release.objects.filter(recordings=self).first()
        title = None
        if release:
            title = release.title
        image = None
        if release and release.image:
            image = release.image.image.url
        if not image:
            image = "/media/images/noconcert.jpg"
        artists = Artist.objects.filter(primary_concerts__recordings=self).values_list('name').all()
        return {
            "concert": title,
            "mainArtists": [item for sublist in artists for item in sublist],
            "name": self.title,
            "image": image,
            "linkToRecording": reverse("hindustani-recording", args=[self.mbid]),
            "collaborators": [],
            "selectedArtists": ""
        }


class InstrumentPerformance(HindustaniStyle, data.models.InstrumentPerformance):
    pass


class Composer(HindustaniStyle, data.models.Composer):
    pass


class ComposerAlias(HindustaniStyle, data.models.ComposerAlias):
    pass


class Lyrics(models.Model):
    lyrics = models.CharField(max_length=50)


class Work(HindustaniStyle, data.models.Work):
    class Meta:
        ordering = ['id']

    lyrics = models.ForeignKey("Lyrics", blank=True, null=True, on_delete=models.CASCADE)


class WorkTime(models.Model):
    # The time in a recording that a work occurs (recordings can consist of
    # many works)
    recording = models.ForeignKey(Recording, on_delete=models.CASCADE)
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    # a worktime is always ordered ...
    sequence = models.IntegerField()
    # but its time is optional (we may not have it yet)
    time = models.IntegerField(blank=True, null=True)


class Raag(data.models.BaseModel, data.models.ImageMixin):
    class Meta:
        ordering = ['id']

    missing_image = "raag.jpg"

    objects = managers.HindustaniRaagManager()

    name = models.CharField(max_length=50)
    common_name = models.CharField(max_length=50)
    uuid = models.UUIDField(db_index=True)
    image = models.ForeignKey(data.models.Image, blank=True, null=True, related_name="%(app_label)s_%(class)s_image", on_delete=models.CASCADE)

    def __str__(self):
        return self.name.capitalize()

    def get_absolute_url(self):
        if self.common_name:
            slug = slugify(self.common_name)
        else:
            slug = slugify(self.name)
        return reverse('hindustani-raag', args=[str(self.uuid), slug])

    def works(self):
        return Work.objects.filter(recording__raags=self).distinct()

    def composers(self):
        return Composer.objects.filter(works__recording__raags=self).distinct()

    def artists(self):
        artistmap = {}
        artistcounter = collections.Counter()
        artists = Artist.objects.filter(primary_concerts__recordings__raags=self)
        for a in artists:
            artistcounter[a.pk] += 1
            if a.pk not in artistmap:
                artistmap[a.pk] = a
        artists = []
        for aid, count in artistcounter.most_common():
            artists.append(artistmap[aid])
        return artists

    def related_items(self, instruments=None, forms=None):
        ret = []
        # raag
        ret.append(("raag", self))
        # artist
        artistcount = 0
        for a in self.artists():
            if artistcount == 5:
                break
            if not instruments or a.main_instrument in instruments:
                ret.append(("artist", a))
                artistcount += 1
        # TODO: Should this only be releases from the shown artists?
        # releases
        releases = Release.objects.filter(recordings__in=self.recording_set.all()).distinct()
        # If forms is set, reduce the releases that are shown
        if forms:
            for f in forms:
                ret.append(("form", f))
            releases = releases.filter(recordings__forms__in=forms)
        for r in releases[:5]:
            ret.append(("release", r))
        # forms (of recordings that also have this raag)
        # But only of recordings in the selected releases
        forms = collections.Counter()
        for tr in self.recording_set.filter(release__in=releases):
            for fo in tr.forms.all():
                forms[fo] += 1
        # TODO: This shows all forms used in releases that have
        # recordings with the specified top level filter forms.
        # This means that there could be more forms than the ones
        # selected. (Are these 'related'?)
        for fo, _ in forms.most_common(5):
            ret.append(("form", fo))
        return ret


class RaagAlias(models.Model):
    name = models.CharField(max_length=50)
    raag = models.ForeignKey("Raag", related_name="aliases", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Taal(data.models.BaseModel, data.models.ImageMixin):
    class Meta:
        ordering = ['id']

    missing_image = "taal.jpg"

    objects = managers.HindustaniTaalManager()

    name = models.CharField(max_length=50)
    common_name = models.CharField(max_length=50)
    num_maatras = models.IntegerField(null=True)
    uuid = models.UUIDField(db_index=True)
    image = models.ForeignKey(data.models.Image, blank=True, null=True, related_name="%(app_label)s_%(class)s_image", on_delete=models.CASCADE)

    def __str__(self):
        return self.name.capitalize()

    def get_absolute_url(self):
        if self.common_name:
            slug = slugify(self.common_name)
        else:
            slug = slugify(self.name)
        return reverse('hindustani-taal', args=[str(self.uuid), slug])

    def percussion_artists(self):
        artistmap = {}
        artistcounter = collections.Counter()
        artists = Artist.objects.filter(
            Q(instrumentperformance__recording__taals=self) & Q(instrumentperformance__instrument__percussion=True))
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

    def related_items(self, layas=None, instruments=None, forms=None):
        ret = []
        # taal
        ret.append(("taal", self))
        # artists
        # TODO: We can only filter by percussion instruments here, do we
        # want to only give these options in the list?
        artistcount = 0
        for a in self.percussion_artists():
            if artistcount == 5:
                break
            if not instruments or a.main_instrument in instruments:
                ret.append(("artist", a))
                artistcount += 1
        # releases
        # TODO: Should this be releases by the shown artists?
        releases = Release.objects.filter(recordings__in=self.recording_set.all()).distinct()
        if layas:
            # TODO: If we select more than 1 taal, and some layas, then
            # these layas will show more than once
            for l in layas:
                ret.append(("laya", l))
            releases = releases.filter(recordings__layas__in=layas)
        for r in releases[:5]:
            ret.append(("release", r))
        # forms (of recordings that also have this taal, filtered by
        # recordings in case we limited with laya)
        forms = collections.Counter()
        for tr in self.recording_set.filter(release__in=releases):
            for fo in tr.forms.all():
                forms[fo] += 1
        for fo, _ in forms.most_common(5):
            ret.append(("form", fo))
        return ret


class TaalAlias(models.Model):
    name = models.CharField(max_length=50)
    taal = models.ForeignKey("Taal", related_name="aliases", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Laya(data.models.BaseModel):
    class Meta:
        ordering = ['id']

    objects = managers.HindustaniLayaManager()

    name = models.CharField(max_length=50)
    common_name = models.CharField(max_length=50)
    uuid = models.UUIDField(db_index=True)

    def __str__(self):
        return self.name.capitalize()

    def get_absolute_url(self):
        if self.common_name:
            slug = slugify(self.common_name)
        else:
            slug = slugify(self.name)
        return reverse('hindustani-laya', args=[str(self.uuid), slug])

    def recordings(self):
        return self.recording_set.all()

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
    laya = models.ForeignKey("Laya", related_name="aliases", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Form(data.models.BaseModel):
    class Meta:
        ordering = ['id']

    objects = managers.HindustaniFormManager()

    name = models.CharField(max_length=50)
    common_name = models.CharField(max_length=50)
    uuid = models.UUIDField(db_index=True)

    def artists(self):
        """ Artists who are the lead artist of a release and
        who perform releases with this form """
        artistmap = {}
        artistcounter = collections.Counter()
        artists = Artist.objects.filter(primary_concerts__recordings__forms=self)
        for a in artists:
            artistcounter[a.pk] += 1
            if a.pk not in artistmap:
                artistmap[a.pk] = a
        artists = []
        for aid, count in artistcounter.most_common():
            artists.append(artistmap[aid])
        return artists

    def __str__(self):
        return self.name.capitalize()

    def get_absolute_url(self):
        if self.common_name:
            slug = slugify(self.common_name)
        else:
            slug = slugify(self.name)
        return reverse('hindustani-form', args=[str(self.uuid), slug])

    def recordings(self):
        return self.recording_set.all()

    def related_items(self, layas=None):
        ret = []
        # form
        ret.append(("form", self))
        # artists
        for a in self.artists()[:5]:
            ret.append(("artist", a))

        # raags (of recordings that also have this form)
        raags = collections.Counter()
        for tr in self.recording_set.all():
            for ra in tr.raags.all():
                raags[ra] += 1
        for ra, _ in raags.most_common(5):
            ret.append(("raag", ra))
        # releases
        releases = Release.objects.filter(recordings__in=self.recording_set.all()).distinct()
        if layas:
            for l in layas:
                ret.append(("laya", l))
            releases = releases.filter(recordings__layas__in=layas)
        for r in releases[:5]:
            ret.append(("release", r))
        return ret


class FormAlias(models.Model):
    name = models.CharField(max_length=50)
    form = models.ForeignKey("Form", related_name="aliases", on_delete=models.CASCADE)

    def __str__(self):
        return self.name
