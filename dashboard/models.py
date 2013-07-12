from django.db import models
from django_extensions.db.fields import UUIDField
from django.core.urlresolvers import reverse

import datetime
import uuid

class StateCarryingManager(models.Manager):
    """ A model manager that also creates a state entry when a
    new object is made. This state object is used to keep track
    of progress on the import.
    """

    def __init__(self, stateclass=None, linkname=None):
        models.Manager.__init__(self)
        self.stateclass = stateclass
        self.linkname = linkname

    def create(self, **kwargs):
        baseobject = models.Manager.create(self, **kwargs)
        if self.stateclass and self.linkname:
            # Use magic **dict because `linkname' changes between models.
            self.stateclass.objects.create(**{self.linkname: baseobject})
        return baseobject

class CompletenessChecker(models.Model):
    """ Stores information about modules that have been written to check
    the completeness and consistency of the data that we have stored in 
    external sources and the audio files.
    See the dashboard.jobs module for more information
    """
    TYPE_CHOICE = ( ('r', 'Release'), ('f', 'File') )
    name = models.CharField(max_length=200)
    module = models.CharField(max_length=200)
    # flag for if this a checker for a single file, or for a whole release
    type = models.CharField(max_length=5, choices=TYPE_CHOICE)

class CollectionState(models.Model):
    """ A collection is processed when all releases linked to it are
    complete
    """
    collection = models.ForeignKey("Collection")
    STATE_CHOICE = ( ('n', 'Not started'), ('s', 'Started'), ('f', 'Finished') )
    state = models.CharField(max_length=10, choices=STATE_CHOICE, default='n')
    state_date = models.DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return "%s (%s)" % (dict(self.STATE_CHOICE)[self.state], self.state_date)

class Collection(models.Model):
    objects = StateCarryingManager()
    objects.stateclass = CollectionState
    objects.linkname = "collection"

    id = UUIDField(primary_key=True)
    name = models.CharField(max_length=200)
    last_updated = models.DateTimeField(default=datetime.datetime.now)
    root_directory = models.CharField(max_length=255)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.id)

    def state_colour(self):
        curr = self.get_current_state()
        if curr:
            if curr.state == "n":
                return "red"
            elif curr.state == "s":
                return "yellow"
            elif curr.state == "f":
                return "green"
        return "red"

    def get_current_state(self):
        return CollectionState.objects.filter(collection=self).order_by('-state_date')[0]

    def status_start(self):
        """ Mark this collection as having its importer started. """
        CollectionState.objects.create(collection=self, state='s')

    def status_can_finish(self):
        """ See if this collection's import can finish.
        An import can finish if all its children directories have finished.
        """
        for rel in self.musicbrainzrelease_set.all():
            relstate = rel.get_current_state()
            if relstate.state != 'f':
                return False
        return True

    def status_finish(self):
        """ Mark this collection as having finished its import.
        This method doesn't check if the import can actually be 
        finished first.
        """
        CollectionState.objects.create(collection=self, state='f')

    def get_absolute_url(self):
        return reverse("dashboard-collection", args=[str(self.id)])

    def add_log_message(self, message):
        return CollectionLogMessage.objects.create(collection=self, message=message)

class CollectionLogMessage(models.Model):
    """ A message that a completeness checker can add to a Collection """
    collection = models.ForeignKey(Collection)
    message = models.TextField()
    datetime = models.DateTimeField(default=datetime.datetime.now)

class MusicbrainzRelease(models.Model):
    id = UUIDField(primary_key=True)
    collection = models.ForeignKey(Collection)
    title = models.CharField(max_length=200)

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.id)

    def get_absolute_url(self):
        return reverse("dashboard-release", args=[str(self.id)])

    def matched_paths(self):
        r = []
        for m in self.collectiondirectory_set.all():
            r.append(m.path)
        return ", ".join(r)

class ReleaseState(models.Model):
    """ Indicates the procesing state of a release. A release has finished
    processing when all files it is part of have finished.

    We link to a CollectionDirectory instead of MusicbrainzRelease
    because it lets us use the same state/log information for
    releases that are not in the collection also.
    """
    release = models.ForeignKey("CollectionDirectory")
    STATE_CHOICE = ( ('n', 'Not started'), ('s', 'Started'), ('f', 'Finished') )
    state = models.CharField(max_length=10, choices=STATE_CHOICE, default='n')
    state_date = models.DateTimeField(default=datetime.datetime.now)
    
class CollectionDirectory(models.Model):
    """ A directory inside the file tree for a collection that has releases
    in it. This usually corresponds to a single CD. This means a MusicbrainzRelease
    may have more than 1 CollectionDirectory """

    objects = StateCarryingManager(ReleaseState, "release")

    collection = models.ForeignKey(Collection)
    musicbrainz_release = models.ForeignKey(MusicbrainzRelease, blank=True, null=True)
    path = models.CharField(max_length=255)
    
    # TODO: __unicode__

    def short_path(self):
        if len(self.path) < 60:
            return self.path
        else:
            return self.path[:30] + "..." + self.path[-30:]

    def get_absolute_url(self):
        return reverse('dashboard-directory', args=[int(self.id)])

    def update_state(self, state):
        rs = ReleaseState.objects.create(release=self, state=state)

    def get_current_state(self):
        return ReleaseState.objects.all().order_by('-state_date')[0]

    def add_log_message(self, checker, message):
        return ReleaseLogMessage.objects.create(release=self, checker=checker, message=message)

class ReleaseLogMessage(models.Model):
    """ A message that a completeness checker can add to a CollectionDirectory """
    release = models.ForeignKey(CollectionDirectory)
    checker = models.ForeignKey(CompletenessChecker, blank=True, null=True)
    message = models.TextField()
    datetime = models.DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return "%s: %s" % (self.datetime, self.message)

class FileState(models.Model):
    """ Indicates the processing state of a single file.
    a file has finished processing when all `file' consistency
    checkers have completed (regardless of if they are good or bad). """

    file = models.ForeignKey("CollectionFile")
    STATE_CHOICE = ( ('n', 'Not started'), ('s', 'Started'), ('f', 'Finished') )
    state = models.CharField(max_length=10, choices=STATE_CHOICE, default='n')
    state_date = models.DateTimeField(default=datetime.datetime.now)

class CollectionFile(models.Model):
    """ A single audio file in the collection. A file is part of a
    collection directory.
    """
    objects = StateCarryingManager(FileState, "file")

    name = models.CharField(max_length=255)
    directory = models.ForeignKey(CollectionDirectory)

    def update_state(self, state):
        rs = FileState.objects.create(file=self, state=state)

    def get_current_state(self):
        return FileState.objects.all().order_by('-state_date')[0]

    def add_log_message(self, checker, message):
        return FileLogMessage.objects.create(file=self, checker=checker, message=message)

    def get_absolute_url(self):
        return reverse('dashboard-file', args=[int(self.id)])

class FileLogMessage(models.Model):
    """ A message that a completeness checker can add to a CollectionFile """
    recording = models.ForeignKey(CollectionFile)
    checker = models.ForeignKey(CompletenessChecker)
    message = models.TextField()
    datetime = models.DateTimeField(default=datetime.datetime.now)

class Status(models.Model):
    """ The result of running a single completeness checker
    on a single file. The a completeness checker either returns 
    True or False.
    """
    STATUS_CHOICE = ( ('s', 'Started'), ('g', 'Good'), ('b', 'Bad') )
    datetime = models.DateTimeField()
    recording = models.ForeignKey(CollectionFile, blank=True, null=True)
    release = models.ForeignKey(MusicbrainzRelease, blank=True, null=True)
    monitor = models.ForeignKey(CompletenessChecker)
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, default='s')
    data = models.TextField(blank=True, null=True)

