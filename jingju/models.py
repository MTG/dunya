import collections
import random

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Count
from django.db.models import Q
from django.utils.text import slugify

import data.models

class Recording(data.models.BaseModel):
    class Meta:
        ordering = ['id']

    title = models.CharField(max_length=200, blank=True, null=True)
    mbid = models.UUIDField(blank=True, null=True)
    work = models.ForeignKey('Work')
    performers = models.ManyToManyField('Artist', through='RecordingPerformer', related_name = 'performer')
    instrumentalists = models.ManyToManyField('Artist', through='RecordingInstrumentalist', related_name = 'instrumentalist')

    def __unicode__(self):
        return u"%s" % (self.title)

class RecordingInstrumentalist(models.Model):
    recording = models.ForeignKey('Recording')
    artist = models.ForeignKey('Artist')
    instrument = models.ForeignKey('Instrument')

class Artist(data.models.Artist):
    role_type = models.ForeignKey('RoleType', blank=True, null=True)
    instrument = models.ForeignKey('Instrument', blank=True, null=True, related_name = 'jingju')

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
    performer = models.ForeignKey('Artist')
    sequence = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return u"%s, seq %d %s" % (self.recording, self.sequence, self.release)


class Work(data.models.BaseModel):
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

class Release(data.models.Release):
    class Meta:
        ordering = ['id']

    recordings = models.ManyToManyField('Recording', through='RecordingRelease')
    performer = models.ForeignKey('Artist', blank=True, null=True)


class RoleType(data.models.BaseModel):
    name = models.CharField(max_length=100)
    uuid = models.UUIDField()

class Play(data.models.BaseModel):
    name = models.CharField(max_length=100)
    uuid = models.UUIDField()

class Score(data.models.BaseModel):
    name = models.CharField(max_length=100)
    uuid = models.UUIDField()

