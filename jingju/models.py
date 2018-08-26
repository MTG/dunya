import collections
import random

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Count
from django.db.models import Q
from django.utils.text import slugify

import data.models
import managers

class Recording(data.models.Recording):
    class Meta:
        ordering = ['id']

    work = models.ForeignKey('Work')
    release = models.ForeignKey('Release', through='RecordingRelease')
    performer = models.ManyToManyField('Performer', through='RecordingPerformer')
    instrumentalists = models.ManyToManyField('Artist', through='RecordingArtist')

class RecordingArtist(models.Model):
    recording = models.ForeignKey('Recording')
    artist = models.ForeignKey('Artist')
    instrument = models.ForeignKey('Instrument')

class Artist(data.models.Artist):
    class Meta:
        ordering = ['id']

class Instrument(data.models.Instrument):
    class Meta:
        ordering = ['id']


class RecordingRelease(models.Model):
    recording = models.ForeignKey('Recording')
    release = models.ForeignKey('Release')
    sequence = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return u"%s, seq %d %s" % (self.recording, self.sequence, self.release)

class RecordingPerformer(models.Model):
    recording = models.ForeignKey('Recording')
    performer = models.ForeignKey('Performer')
    sequence = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return u"%s, seq %d %s" % (self.recording, self.sequence, self.release)


class Work(data.models.Work):
    class Meta:
        ordering = ['id']

    score = models.ForeignKey('Score', blank=True, null=True)
    play = models.ForeignKey('Play', blank=True, null=True)

    def recordings(self):
        return self.recording_set.all()

class Release(data.models.Release):
    class Meta:
        ordering = ['id']

    recordings = models.ManyToManyField('Recording', through='RecordingRelease')
    performer = models.ForeignKey('Performer', blank=True, null=True)

class Performer(data.models.BaseModel):
    class Meta:
        ordering = ['id']

    name = models.CharField(max_length=100)
    uuid = models.UUIDField()
    recordings = models.ManyToManyField('Recording', through='RecordingPerformer')
    roletype = models.ForeignKey('Roletype',  blank=True, null=True)

class Roletype(data.models.BaseModel):
    name = models.CharField(max_length=100)

class Play(data.models.BaseModel):
    name = models.CharField(max_length=100)
    uuid = models.UUIDField()

class Score(data.models.BaseModel):
    name = models.CharField(max_length=100)
    uuid = models.UUIDField()

