from django.db import models
from django_extensions.db.fields import UUIDField

import datetime
import uuid

class Collection(models.Model):
    id = UUIDField(primary_key=True)
    name = models.CharField(max_length=200)
    last_updated = models.DateTimeField(default=datetime.datetime.now)
    root_directory = models.CharField(max_length=255)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.id)

class MusicbrainzRelease(models.Model):
    id = UUIDField(primary_key=True)
    collection = models.ForeignKey(Collection)
    title = models.CharField(max_length=200)

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.id)

class CollectionDirectory(models.Model):
    """ A directory inside the file tree for a collection that has releases
    in it. This usually corresponds to a single CD. """
    # TODO: If we have different folders per release (multi CDs?) or are they
    # all in one directory?
    collection = models.ForeignKey(Collection)
    musicbrainz_release = models.ForeignKey(MusicbrainzRelease, blank=True, null=True)
    path = models.CharField(max_length=255)

class CollectionFile(models.Model):
    name = models.CharField(max_length=255)
    directory = models.ForeignKey(CollectionDirectory)

class FileState(models.Model):
    """ Indicates the processing state of a single file.
    a file has finished processing when all `file' consistency
    checkers have completed (regardless of if they are good or bad). """
    file = models.ForeignKey(CollectionFile)
    STATE_CHOICE = ( ('n', 'Not started'), ('s', 'Started'), ('f', 'Finished') )
    status = models.CharField(max_length=10, choices=STATE_CHOICE, default='n')
    status_date = models.DateTimeField(default=datetime.datetime.now)

class ReleaseState(models.Model):
    """ Indicates the procesing state of a release. A release has finished
    processing when all files it is part of have finished.

    We link to a CollectionDirectory instead of MusicbrainzRelease
    because it lets us use the same state/log information for
    releases that are not in the collection also.
    """
    release = models.ForeignKey(CollectionDirectory)
    STATE_CHOICE = ( ('n', 'Not started'), ('s', 'Started'), ('f', 'Finished') )
    status = models.CharField(max_length=10, choices=STATE_CHOICE, default='n')
    status_date = models.DateTimeField(default=datetime.datetime.now)

class CollectionState(models.Model):
    """ A collection is processed when all releases linked to it are
    complete
    """
    collection = models.ForeignKey(Collection)
    STATE_CHOICE = ( ('n', 'Not started'), ('s', 'Started'), ('f', 'Finished') )
    status = models.CharField(max_length=10, choices=STATE_CHOICE, default='n')
    status_date = models.DateTimeField(default=datetime.datetime.now)

class ConsistencyChecker(models.Model):
    name = models.CharField(max_length=200)
    pythonclass = models.CharField(max_length=200)
    typeofentity = models.CharField(max_length=50)

class Status(models.Model):
    """ Applying a single consitensy checker to a single file """
    STATUSCHOICE = ( ('s', 'Started'), ('g', 'Good'), ('b', 'Bad') )
    datetime = models.DateTimeField()
    recording = models.ForeignKey(CollectionFile)
    monitor = models.ForeignKey(HealthMonitor)
    status = models.CharField(max_length=10, choices=STATUSCHOICE, default='s')

class FileLogMessage(models.Model):
    recording = models.ForeignKey(CollectionFile)
    monitor = models.ForeignKey(HealthMonitor, blank=True, null=True)
    message = models.TextField()
    datetime = models.DateTimeField()

class ReleaseLogMessage(models.Model):
    release = models.ForeignKey(CollectionDirectory)
    monitor = models.ForeignKey(HealthMonitor, blank=True, null=True)
    message = models.TextField()
    datetime = models.DateTimeField()
