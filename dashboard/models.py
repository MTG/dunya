from django.db import models
from django_extensions.db.fields import UUIDField
from django.core.urlresolvers import reverse
from django.db.models.loading import get_model

import datetime
import uuid
import os

class StateCarryingManager(models.Manager):
    """ A model manager that also creates a state entry when a
    new object is made. This state object is used to keep track
    of progress on the import.
    """

    def create(self, **kwargs):
        if not self.stateclass or not self.linkname:
            raise ValueError("Need stateclass and linkname set in a subclass")
        if isinstance(self.stateclass, basestring):
            cls = get_model("dashboard", self.stateclass)
        else:
            cls = self.stateclass
        if not cls:
            raise ValueError("Stateclass should be a type that exists")
        baseobject = models.Manager.create(self, **kwargs)
        # Use magic **dict because `linkname' changes between models.
        cls.objects.create(**{self.linkname: baseobject})
        return baseobject

    def get_or_create(self, **kwargs):
        if not self.stateclass or not self.linkname:
            raise ValueError("Need stateclass and linkname set in a subclass")
        if isinstance(self.stateclass, basestring):
            cls = get_model("dashboard", self.stateclass)
        else:
            cls = self.stateclass
        if not cls:
            raise ValueError("Stateclass should be a type that exists")
        baseobject, created = models.Manager.get_or_create(self, **kwargs)
        if created:
            cls.objects.create(**{self.linkname: baseobject})
        return baseobject, created

class CollectionManager(StateCarryingManager):
    stateclass = "CollectionState"
    linkname = "collection"

class CollectionFileManager(StateCarryingManager):
    stateclass = "CollectionFileState"
    linkname = "collectionfile"

class MusicbrainzReleaseManager(StateCarryingManager):
    stateclass = "MusicbrainzReleaseState"
    linkname = "musicbrainzrelease"

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

    def __unicode__(self):
        return "%s (%s / %s)" % (self.name, self.module, self.type)

class CollectionState(models.Model):
    """ A collection is processed when all releases linked to it are
    complete
    """
    collection = models.ForeignKey("Collection")
    STATE_CHOICE = ( ('n', 'Not started'), ('i', 'Importing'),
            ('s', 'Started'), ('f', 'Finished') )
    state = models.CharField(max_length=10, choices=STATE_CHOICE, default='n')
    state_date = models.DateTimeField(default=datetime.datetime.now)

    @property
    def state_name(self):
        return dict(self.STATE_CHOICE)[self.state]

    def __unicode__(self):
        return "%s (%s)" % (self.state_name, self.state_date)

class Test(models.Model):
    def __init__(self, **kwargs):
        import django.db
        raise django.db.IntegrityError("oops")

class Collection(models.Model):

    objects = CollectionManager()

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
        return self.collectionstate_set.order_by('-state_date').all()[0]

    def set_status_importing(self):
        CollectionState.objects.create(collection=self, state='i')

    def set_status_start(self):
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

    def set_status_finish(self):
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

class MusicbrainzReleaseState(models.Model):
    """ Indicates the procesing state of a release. A release has finished
    processing when all files it is part of have finished.
    """
    musicbrainzrelease = models.ForeignKey("MusicbrainzRelease")
    STATE_CHOICE = ( ('n', 'Not started'), ('s', 'Started'), ('f', 'Finished') )
    state = models.CharField(max_length=10, choices=STATE_CHOICE, default='n')
    state_date = models.DateTimeField(default=datetime.datetime.now)
    
    @property
    def state_name(self):
        return dict(self.STATE_CHOICE)[self.state]

    def __unicode__(self):
        return "%s (%s)" % (self.state_name, self.state_date)

class MusicbrainzRelease(models.Model):

    objects = MusicbrainzReleaseManager()

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
            r.append(m.short_path())
        return r

    def update_state(self, state):
        rs = MusicbrainzReleaseState.objects.create(musicbrainzrelease=self, state=state)

    def start_state(self):
        self.update_state('s')

    def try_finish_state(self):
        """ Check the state of all of this release's files, and also
            the state of the release-specific jobs. """
        currentstate = self.get_current_state()
        if currentstate.state == 's':
            files = CollectionFileState.objects.filter(directory__musicbrainzrelease=self).exclude(state=f)
            if not files.count():
                self.update_state('f')
        # TODO: Bubble up to the collection

    def get_current_state(self):
        states = self.musicbrainzreleasestate_set.order_by('-state_date').all()
        if not len(states):
            raise Exception("eoo, no states")
        return states[0]

class CollectionDirectory(models.Model):
    """ A directory inside the file tree for a collection that has releases
    in it. This usually corresponds to a single CD. This means a MusicbrainzRelease
    may have more than 1 CollectionDirectory """

    collection = models.ForeignKey(Collection)
    musicbrainzrelease = models.ForeignKey(MusicbrainzRelease, blank=True, null=True)
    path = models.CharField(max_length=255)

    @property
    def full_path(self):
        return os.path.join(self.collection.root_directory, self.path)
    
    def __unicode__(self):
        return "From collection %s, release %s, path on disk %s" % (self.collection,
                self.musicbrainzrelease, self.path)

    def short_path(self):
        if len(self.path) < 60:
            return self.path
        else:
            return u"%s\u2026%s" % (self.path[:30], self.path[-30:])

    def get_absolute_url(self):
        return reverse('dashboard-directory', args=[int(self.id)])

    def add_log_message(self, checker, message):
        return ReleaseLogMessage.objects.create(release=self, checker=checker, message=message)

    def get_file_list(self):
        return self.collectionfile_set.order_by('name').all()

class ReleaseLogMessage(models.Model):
    """ A message that a completeness checker can add to a CollectionDirectory """
    release = models.ForeignKey(CollectionDirectory)
    checker = models.ForeignKey(CompletenessChecker, blank=True, null=True)
    message = models.TextField()
    datetime = models.DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return "%s: %s" % (self.datetime, self.message)

class CollectionFileState(models.Model):
    """ Indicates the processing state of a single file.
    a file has finished processing when all `file' consistency
    checkers have completed (regardless of if they are good or bad). """

    collectionfile = models.ForeignKey("CollectionFile")
    STATE_CHOICE = ( ('n', 'Not started'), ('s', 'Started'), ('f', 'Finished') )
    state = models.CharField(max_length=10, choices=STATE_CHOICE, default='n')
    state_date = models.DateTimeField(default=datetime.datetime.now)

    @property
    def state_name(self):
        return dict(self.STATE_CHOICE)[self.state]

    def __unicode__(self):
        return "%s (%s)" % (self.state_name, self.state_date)

class CollectionFile(models.Model):
    """ A single audio file in the collection. A file is part of a
    collection directory.
    """
    objects = CollectionFileManager()

    name = models.CharField(max_length=255)
    directory = models.ForeignKey(CollectionDirectory)

    @property
    def path(self):
        return os.path.join(self.directory.collection.root_directory,
                self.directory.path, self.name)

    def start_state(self):
        self.update_state('s')

    def __unicode__(self):
        return "%s (from %s)" % (self.name, self.directory.musicbrainzrelease)

    def try_finish_state(self):
        """ Check this file's """
        currentstate = self.get_current_state()
        if currentstate.state == 's':
            # If we're in s and there are no more n or s, then we can
            # change to f
            if not self.filestatus_set.filter(status__in=('n', 's')).count():
                self.update_state('f')
        # Bubble up to the directory/release
        self.directory.musicbrainzrelease.try_finish_state()

    def update_state(self, state):
        rs = CollectionFileState.objects.create(collectionfile=self, state=state)

    def get_current_state(self):
        states = self.collectionfilestate_set.order_by('-state_date').all()
        if not len(states):
            raise Exception("eoo, no states")
        return states[0]

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

class FileStatus(models.Model):
    """ The result of running a single completeness checker
    on a single file. The a completeness checker either returns 
    True or False.
    """
    STATUS_CHOICE = ( ('n', 'Not started'), ('s', 'Started'), ('g', 'Good'), ('b', 'Bad') )
    datetime = models.DateTimeField(default=datetime.datetime.now)
    file = models.ForeignKey(CollectionFile, blank=True, null=True)
    checker = models.ForeignKey(CompletenessChecker)
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, default='n')
    data = models.TextField(blank=True, null=True)

    def get_status_icon(self):
        icons = {"n": "stop.png",
                 "s": "time_go.png",
                 "g": "tick.png",
                 "b": "cross.png"
                }
        return icons[self.status]

    def get_status_desc(self):
        return dict(self.STATUS_CHOICE)[self.status]

class ReleaseStatus(models.Model):
    """ The result of running a single completeness checker
    on a single release. The a completeness checker either returns 
    True or False.
    """
    STATUS_CHOICE = ( ('n', 'Not started'), ('s', 'Started'), ('g', 'Good'), ('b', 'Bad') )
    datetime = models.DateTimeField(default=datetime.datetime.now)
    release = models.ForeignKey(MusicbrainzRelease, blank=True, null=True)
    checker = models.ForeignKey(CompletenessChecker)
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, default='n')
    data = models.TextField(blank=True, null=True)

    def get_status_icon(self):
        icons = {"n": "stop.png",
                 "s": "time_go.png",
                 "g": "tick.png",
                 "b": "cross.png"
                }
        return icons[self.status]

    def get_status_desc(self):
        return dict(self.STATUS_CHOICE)[self.status]
