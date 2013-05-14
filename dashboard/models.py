from django.db import models
from django_extensions.db.fields import UUIDField

import datetime
import uuid

class MusicbrainzCollection(models.Model):
    id = UUIDField(primary_key=True)
    name = models.CharField(max_length=200)
    last_updated = models.DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.id)

class MusicbrainzRelease(models.Model):
    id = UUIDField(primary_key=True)
    collection = models.ForeignKey(MusicbrainzCollection)
    title = models.CharField(max_length=200)

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.id)

class MusicbrainzRecording(models.Model):
    id = UUIDField(primary_key=True)
    release = models.ForeignKey(MusicbrainzRelease)
    title = models.CharField(max_length=200)
    position = models.IntegerField()

    def __unicode__(self):
        return "%s: %s (%s)" % (self.position, self.title, self.id)

class HealthMonitor(models.Model):
    name = models.CharField(max_length=200)
    pythonclass = models.CharField(max_length=200)

class Status(models.Model):
    STATUSCHOICE = ( ('g', 'Good'), ('b', 'Bad') )
    datetime = models.DateTimeField()
    recording = models.ForeignKey(MusicbrainzRecording)
    monitor = models.ForeignKey(HealthMonitor)
    status = models.CharField(max_length=10, choices=STATUSCHOICE)

class LogMessage(models.Model):
    recording = models.ForeignKey(MusicbrainzRecording)
    monitor = models.ForeignKey(HealthMonitor)
    message = models.TextField()
    datetime = models.DateTimeField()
