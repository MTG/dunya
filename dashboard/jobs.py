from django.db import transaction
import celery

from dashboard.models import *
import compmusic

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
