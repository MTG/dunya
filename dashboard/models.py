from django.db import models
from django_extensions.db.fields import UUIDField

import uuid

class MusicbrainzCollection(models.Model):
    id = UUIDField(primary_key=True)
    name = models.CharField(max_length=200)
    last_updated = models.DateTimeField()

class MusicbrainzRelease(models.Model):
    collectionid = models.ForeignKey(MusicbrainzCollection)
    id = UUIDField(primary_key=True)
    name = models.CharField(max_length=200)

class MusicbrainzRecording(models.Model):
    id = UUIDField(primary_key=True)
    name = models.CharField(max_length=200)
    position = models.IntegerField()

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
