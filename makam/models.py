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
from typing import Optional, List

import unidecode
from django.urls import reverse
from django.db import models
from django.db.models import Q
from django.utils.text import slugify

import data.models
from makam import managers


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
    class Meta:
        ordering = ['id']

    def collaborating_artists(self):
        our_releases = Release.objects.filter(
            Q(recordings__instrumentperformance__artist=self) | Q(artists=self)).distinct()
        others = Artist.objects.filter(Q(instrumentperformance__recording__release__in=our_releases) | Q(
            primary_concerts__in=our_releases)).exclude(pk=self.pk).distinct()
        counts = collections.Counter(others)
        return [a for a, c in counts.most_common(10)]

    def main_releases(self, collection_ids: Optional[List[str]]=None, permission=False):
        """ Releases where this artist is named on the cover """
        if not permission:
            permission = ["U"]

        return self.primary_concerts.with_permissions(collection_ids, permission).all()

    def accompanying_releases(self):
        """ Releases where this artist performs, but isn't named on the cover """
        return Release.objects.filter(recordings__instrumentperformance__artist=self).exclude(
            id__in=self.primary_concerts.all()).distinct()


class ComposerAlias(MakamStyle, data.models.ComposerAlias):
    pass


class Composer(MakamStyle, data.models.Composer):
    class Meta:
        ordering = ['id']

    def worklist(self):
        return self.works.all()

    def lyricworklist(self):
        return self.lyric_works.all()


class Release(MakamStyle, data.models.Release):
    class Meta:
        ordering = ['id']

    is_concert = models.BooleanField(default=False)
    recordings = models.ManyToManyField('Recording', through="ReleaseRecording")
    collection = models.ForeignKey('data.Collection', blank=True, null=True, related_name="makam_releases", on_delete=models.CASCADE)

    objects = managers.CollectionReleaseManager()

    def tracklist(self):
        """Return an ordered list of recordings in this release"""
        return self.recordings.order_by('releaserecording')

    def instruments_for_artist(self, artist):
        """ Returns a list of instruments that this
        artist performs on this release."""
        return Instrument.objects.filter(instrumentperformance__artist=artist,
                                         instrumentperformance__recording__release=self).distinct()

    def performers(self):
        """ The performers on a release are those who are in the performance
        relations, and the lead artist of the release (if not in relations)
        """
        artists = self.artists.all()
        performers = Artist.objects.filter(instrumentperformance__recording__release=self).exclude(
            id__in=artists).distinct()
        return list(artists) + list(performers)


class ReleaseRecording(models.Model):
    release = models.ForeignKey('Release', on_delete=models.CASCADE)
    recording = models.ForeignKey('Recording', on_delete=models.CASCADE)
    # The number that the track comes in the release. Numerical 1-n
    track = models.IntegerField()

    class Meta:
        ordering = ("track",)

    def __str__(self):
        return u"%s: %s from %s" % (self.track, self.recording, self.release)


class RecordingWork(models.Model):
    work = models.ForeignKey("Work", on_delete=models.CASCADE)
    recording = models.ForeignKey("Recording", on_delete=models.CASCADE)
    sequence = models.IntegerField()

    class Meta:
        ordering = ("sequence",)

    def __str__(self):
        return u"%s: %s" % (self.sequence, self.work.title)


class Recording(MakamStyle, data.models.Recording):
    class Meta:
        ordering = ['id']

    works = models.ManyToManyField("Work", through="RecordingWork")
    artists = models.ManyToManyField("Artist", related_name="recordings_artist")

    # the form Taksim refers to an instrumental improvisation
    has_taksim = models.BooleanField(default=False)
    # and form gazel is a vocal improvisation
    has_gazel = models.BooleanField(default=False)
    # If either of these flags is set, we don't have a work to store
    # the `makam` field to, so we store it here. Only use this field
    # if one of the above two flags are set.
    makam = models.ManyToManyField("Makam", blank=True)
    analyse = models.BooleanField(default=True)
    has_lyrics = models.BooleanField(default=False)

    objects = managers.CollectionRecordingManager()

    def makamlist(self):
        makams = set()
        if self.has_taksim or self.has_gazel:
            makams.update(self.makam.all())
        for w in self.works.all():
            makams.update(w.makam.all())
        return list(makams)

    def usullist(self):
        usuls = set()
        for w in self.works.all():
            usuls.update(w.usul.all())
        return list(usuls)

    def releaselist(self):
        return self.release_set.all()

    def worklist(self):
        return self.works.all()

    def instruments_for_artist(self, artist):
        """ Returns a list of instruments that this
        artist performs on this release."""
        return Instrument.objects.filter(instrumentperformance__artist=artist,
                                         instrumentperformance__recording=self).distinct()

    def performers(self):
        """ The performers on a recording are those who are in the performance
        relations, and the lead artist of the recording's release (if not in relations)
        """
        artists = Artist.objects.filter(primary_concerts__recordings=self).distinct()
        performers = Artist.objects.filter(instrumentperformance__recording=self).exclude(id__in=artists).distinct()
        return list(artists) + list(performers)

    def get_dict(self):
        release = self.release_set.first()
        title = None
        if release:
            title = release.title
        image = None
        if release and release.image:
            image = release.image.image.url
        if not image:
            image = "/static/makam/img/disc1.png"
        artists = Artist.objects.filter(primary_concerts__recordings=self).values_list('name').all()
        return {
            "concert": title,
            "mainArtists": [item for sublist in artists for item in sublist],
            "name": self.title,
            "image": image,
            "linkToRecording": reverse("makam-recording", args=[str(self.mbid)]),
            "collaborators": [],
            "selectedArtists": ""
        }


class InstrumentPerformance(MakamStyle, data.models.InstrumentPerformance):
    pass


class InstrumentManager(models.Manager):
    """ A manager that has a hacky "alias" system - if the requested name is
    a known alias, change it """

    def alias_get(self, name):
        name = name.lower()
        # vocals are credited in mb as "vocals", but we want
        # to call the instrument 'voice'
        if name.startswith("vocal"):
            name = "voice"

        return super(InstrumentManager, self).get(name__iexact=name)


class Instrument(MakamStyle, data.models.Instrument):
    class Meta:
        ordering = ['id']

    # Name in Turkish
    name_tr = models.CharField(max_length=50)

    objects = InstrumentManager()


class MakamAlias(models.Model):
    name = models.CharField(max_length=100)
    makam = models.ForeignKey("Makam", related_name="aliases", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Makam(models.Model):
    class Meta:
        ordering = ['id']

    name = models.CharField(max_length=100)
    tonic_symbol = models.CharField(max_length=50, null=True, blank=True)

    # name in the mu2 files in symtr collection
    mu2_name = models.CharField(max_length=250, null=True, blank=True)
    # string used to identify a makam in the symtr filename
    symtr_key = models.CharField(max_length=250, null=True, blank=True)
    uuid = models.UUIDField(db_index=True)

    objects = managers.MakamFuzzyManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        if isinstance(self.name, unicode):
            mname = unidecode.unidecode(self.name)
        else:
            mname = self.name
        return reverse('makam-makam', args=[str(self.uuid), slugify(mname)])

    def worklist(self):
        return self.work_set.all()

    def taksimlist(self):
        return self.recording_set.filter(has_taksim=True)

    def gazellist(self):
        return self.recording_set.filter(has_gazel=True)


class UsulAlias(models.Model):
    name = models.CharField(max_length=100)
    usul = models.ForeignKey("Usul", related_name="aliases", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Usul(models.Model):
    class Meta:
        ordering = ['id']

    name = models.CharField(max_length=100)
    uuid = models.UUIDField(db_index=True)

    objects = managers.MakamUsulManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        if isinstance(self.name, unicode):
            uname = unidecode.unidecode(self.name)
        else:
            uname = self.name
        return reverse('makam-usul', args=[str(self.uuid), slugify(uname)])

    def worklist(self):
        return self.work_set.all()

    def taksimlist(self):
        if self.name.lower() != "serbest":
            return []
        return Recording.objects.filter(has_taksim=True)

    def gazellist(self):
        if self.name.lower() != "serbest":
            return []
        return Recording.objects.filter(has_gazel=True)


class FormAlias(models.Model):
    name = models.CharField(max_length=100)
    form = models.ForeignKey("Form", related_name="aliases", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Form(models.Model):
    class Meta:
        ordering = ['id']

    name = models.CharField(max_length=100)
    uuid = models.UUIDField(db_index=True)

    objects = managers.MakamFormManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        if isinstance(self.name, unicode):
            fname = unidecode.unidecode(self.name)
        else:
            fname = self.name
        return reverse('makam-form', args=[str(self.uuid), slugify(fname)])

    def worklist(self):
        return self.work_set.all()


class Work(MakamStyle, data.models.Work):
    class Meta:
        ordering = ['id']

    composition_date = models.CharField(max_length=100, blank=True, null=True)

    makam = models.ManyToManyField(Makam, blank=True)
    usul = models.ManyToManyField(Usul, blank=True)
    form = models.ManyToManyField(Form, blank=True)

    def recordinglist(self):
        return self.recording_set.all()

    def makamlist(self):
        return self.makam.all()

    def usullist(self):
        return self.usul.all()

    def formlist(self):
        return self.form.all()

    def composerlist(self):
        return self.composers.all()

    def lyricistlist(self):
        return self.lyricists.all()


class SymbTr(models.Model):
    class Meta:
        ordering = ['id']

    name = models.CharField(max_length=200)
    # We use a uuid directly instead of a link to an existing model
    # because this could be a workid (most common), or a recordingid (sometimes)
    uuid = models.UUIDField(db_index=True)

    def __str__(self):
        return u"%s -> %s" % (self.uuid, self.name)
