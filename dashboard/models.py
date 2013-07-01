from django.db import models
from django_extensions.db.fields import UUIDField

import datetime
import uuid

class CompletenessChecker(models.Model):

    TYPE_CHOICE = ( ('r', 'Release'), ('f', 'File') )
    name = models.CharField(max_length=200)
    module = models.CharField(max_length=200)
    # Is this a checker for a single file, or for a whole release
    type = models.CharField(max_length=5, choices=TYPE_CHOICE)

class Collection(models.Model):
    id = UUIDField(primary_key=True)
    name = models.CharField(max_length=200)
    last_updated = models.DateTimeField(default=datetime.datetime.now)
    root_directory = models.CharField(max_length=255)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.id)

class CollectionState(models.Model):
    """ A collection is processed when all releases linked to it are
    complete
    """
    collection = models.ForeignKey(Collection)
    STATE_CHOICE = ( ('n', 'Not started'), ('s', 'Started'), ('f', 'Finished') )
    state = models.CharField(max_length=10, choices=STATE_CHOICE, default='n')
    state_date = models.DateTimeField(default=datetime.datetime.now)

class MusicbrainzRelease(models.Model):
    id = UUIDField(primary_key=True)
    collection = models.ForeignKey(Collection)
    title = models.CharField(max_length=200)

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.id)

class CollectionDirectory(models.Model):
    """ A directory inside the file tree for a collection that has releases
    in it. This usually corresponds to a single CD. This means a MusicbrainzRelease
    may have more than 1 CollectionDirectory """
    collection = models.ForeignKey(Collection)
    musicbrainz_release = models.ForeignKey(MusicbrainzRelease, blank=True, null=True)
    path = models.CharField(max_length=255)

    def update_state(self, state):
        rs = ReleaseState.objects.create(release=self, state=state)

    def get_current_state(self):
        return ReleaseState.objects.all().order_by('-state_date')[0]

    def add_log_message(self, checker, message):
        return ReleaseLogMessage.objects.create(release=self, checker=checker, message=message)

class ReleaseState(models.Model):
    """ Indicates the procesing state of a release. A release has finished
    processing when all files it is part of have finished.

    We link to a CollectionDirectory instead of MusicbrainzRelease
    because it lets us use the same state/log information for
    releases that are not in the collection also.
    """
    release = models.ForeignKey(CollectionDirectory)
    STATE_CHOICE = ( ('n', 'Not started'), ('s', 'Started'), ('f', 'Finished') )
    state = models.CharField(max_length=10, choices=STATE_CHOICE, default='n')
    state_date = models.DateTimeField(default=datetime.datetime.now)
    
class ReleaseLogMessage(models.Model):
    """ A message that a completeness checker can add to a CollectionDirectory """
    release = models.ForeignKey(CollectionDirectory)
    checker = models.ForeignKey(CompletenessChecker)
    message = models.TextField()
    datetime = models.DateTimeField(default=datetime.datetime.now)

class CollectionFile(models.Model):
    name = models.CharField(max_length=255)
    directory = models.ForeignKey(CollectionDirectory)

    def update_state(self, state):
        rs = FileState.objects.create(file=self, state=state)

    def get_current_state(self):
        return FileState.objects.all().order_by('-state_date')[0]

    def add_log_message(self, checker, message):
        return FileLogMessage.objects.create(file=self, checker=checker, message=message)

class FileState(models.Model):
    """ Indicates the processing state of a single file.
    a file has finished processing when all `file' consistency
    checkers have completed (regardless of if they are good or bad). """
    file = models.ForeignKey(CollectionFile)
    STATE_CHOICE = ( ('n', 'Not started'), ('s', 'Started'), ('f', 'Finished') )
    state = models.CharField(max_length=10, choices=STATE_CHOICE, default='n')
    state_date = models.DateTimeField(default=datetime.datetime.now)

class FileLogMessage(models.Model):
    """ A message that a completeness checker can add to a CollectionFile """
    recording = models.ForeignKey(CollectionFile)
    checker = models.ForeignKey(CompletenessChecker)
    message = models.TextField()
    datetime = models.DateTimeField(default=datetime.datetime.now)

class Status(models.Model):
    """ Applying a single completeness checker to a single file """
    STATUS_CHOICE = ( ('s', 'Started'), ('g', 'Good'), ('b', 'Bad') )
    datetime = models.DateTimeField()
    recording = models.ForeignKey(CollectionFile)
    monitor = models.ForeignKey(CompletenessChecker)
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, default='s')

