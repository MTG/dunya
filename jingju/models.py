# Copyright 2018 Honglin Ma
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


from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Count
from django.db.models import Q
from django.utils.text import slugify
import managers

import data.models

class JingjuStyle(object):
    def get_style(self):
        return "jingju"

    def get_object_map(self, key):
        return {
                "performance": RecordingInstrumentalist,
                "release": Release,
                "artist": Artist,
                "recording": Recording,
                "work": Work,
                "instrument": Instrument
                }[key]

class Recording(JingjuStyle, data.models.BaseModel):
    class Meta:
        ordering = ['id']

    title = models.CharField(max_length=200, blank=True, null=True)
    mbid = models.UUIDField(blank=True, null=True)
    work = models.ForeignKey('Work', null=True)
    performers = models.ManyToManyField('Artist')
    instrumentalists = models.ManyToManyField('Artist', through='RecordingInstrumentalist', related_name = 'instrumentalist')
    shengqiangbanshi = models.ManyToManyField('ShengqiangBanshi')
    objects = managers.CollectionRecordingManager()



    def __unicode__(self):
        return u"%s" % (self.title)

class RecordingInstrumentalist(JingjuStyle, models.Model):
    recording = models.ForeignKey('Recording')
    artist = models.ForeignKey('Artist')
    instrument = models.ForeignKey('Instrument')


class Artist(data.models.Artist):
    alias = models.CharField(max_length=200, blank=True, null=True)
    role_type = models.ForeignKey('RoleType', blank=True, null=True)
    instrument = models.ForeignKey('Instrument', blank=True, null=True, related_name = 'jingju')
    objects = managers.ArtistManager()

    class Meta:
        ordering = ['id']

class ArtistAlias(data.models.ArtistAlias):
    pass

class Instrument(data.models.Instrument):
    class Meta:
        ordering = ['id']


class RecordingRelease(models.Model):
    recording = models.ForeignKey('Recording')
    release = models.ForeignKey('Release')
    sequence = models.IntegerField(blank=True, null=True)

    # The number that the track comes in the concert. Numerical 1-n
    track = models.IntegerField(blank=True, null=True)
    # The disc number. 1-n
    disc = models.IntegerField(blank=True, null=True)
    # The track number within this disc. 1-n
    disctrack = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ("track",)

    def __unicode__(self):
        return u"%s: %s from %s" % (self.track, self.recording, self.release)




class Work(JingjuStyle, data.models.BaseModel):
    class Meta:
        ordering = ['id']

    title = models.CharField(max_length=200, blank=True, null=True)
    mbid = models.UUIDField(blank=True, null=True)
    score = models.ForeignKey('Score', blank=True, null=True)
    play = models.ForeignKey('Play', blank=True, null=True)

    # def recordings(self):
    #     return self.recording_set.all()

    def __unicode__(self):
        return u"%s" % (self.title)

class Release(JingjuStyle, data.models.Release):
    class Meta:
        ordering = ['id']

    recordings = models.ManyToManyField('Recording', through='RecordingRelease')
    # performer = models.ForeignKey('Artist', blank=True, null=True)
    collection = models.ForeignKey('data.Collection', blank=True, null=True)
    objects = managers.CollectionReleaseManager()

class RoleType(data.models.BaseModel):
    name = models.CharField(max_length=100)
    transliteration = models.CharField(max_length=100)
    uuid = models.UUIDField()

class Play(data.models.BaseModel):
    title = models.CharField(max_length=100)
    uuid = models.UUIDField(blank=True, null=True)

class Score(data.models.BaseModel):
    name = models.CharField(max_length=100)
    uuid = models.UUIDField(blank=True, null=True)

class ShengqiangBanshi(data.models.BaseModel):
    name = models.CharField(max_length=100)
    # uuid = models.UUIDField(blank=True, null=True)
