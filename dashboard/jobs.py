from django.db import transaction
import celery

from dashboard.models import *
import compmusic

class DunyaStatusFileTask(celery.Task):
    """ A celery task that performs a health check on a file """
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        pass


class DunyaStatusReleaseTask(celery.Task):
    """ A celery task that performs a health check on a directory
    representing a release """
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        pass

@celery.task(base=DunyaFileTask)
def check_coverart_file(filestate_id, fname):
    """ Check that a file has embedded coverart """
    pass

@celery.task(base=DunyaReleaseTask)
def check_coverart_release(releasestate_id, releaseid, releasedir):
    """ Check that a release has coverart on the CAA """
    pass

@celery.task(base=DunyaFileTask)
def check_tags_file(filestate_id, fname):
    """ Check that a file has all the correct musicbrainz tags """
    pass

@celery.task(base=DunyaReleaseTask)
def check_release_relationships(releasestate_id, releaseid, releasedir):
    """ Check that a release on MB has relationships for composers,
    performers, and wikipedia links. """
    pass

@celery.task()
def load_musicbrainz_collection(collectionid):
    """ Load a musicbrainz collection into the database.
    TODO: what if the collectionid doesn't exist
    - Need to log files with no release and 
           release with no files
    """
    releases = compmusic.get_releases_in_collection(collectionid)
    with transaction.commit_on_success():
        coll = MusicbrainzCollection.objects.create(id=collectionid)
        for relid in releases:
            print "."
            try:
                mbrelease = compmusic.mb.get_release_by_id(relid, includes=["recordings"])
                mbrelease = mbrelease["release"]
                title = mbrelease["title"]
                rel = MusicbrainzRelease.objects.create(id=relid, collection=coll, title=title)
                tracks = []
                position = 1
                for medium in mbrelease.get("medium-list"):
                    for track in medium.get("track-list"):
                        trackid = track["recording"]["id"]
                        tracktitle = track["recording"]["title"]
                        tr = MusicbrainzRecording.objects.create(id=trackid, release=rel, title=tracktitle, position=position)
                        position += 1
            except: # TODO: correct mb error here
                print "missing", relid
                # TODO: log error message
