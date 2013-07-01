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

class CompletenessBase(object):
    pass

class CoverartFile(CompletenessBase):
    """ Check that a file has embedded coverart """
    type = 'f'

    @celery.task(base=DunyaFileTask, ignore_result=True)
    def task(collectionfile_id):
        fg = CollectionFile.objects.get(pk=collectionfile_id)

class CoverartRelease(CompletenessBase):
    """ Check that a release has coverart on the CAA """
    type = 'r'

    @celery.task(base=DunyaReleaseTask, ignore_result=True)
    def task(releasestate_id, releaseid, releasedir):
        pass

class FileTags(CompletenessBase):
    """ Check that a file has all the correct musicbrainz tags """
    type = 'f'

    @celery.task(base=DunyaFileTask, ignore_result=True)
    def task(filestate_id, fname):
        pass

class ReleaseRelationships(CompletenessBase):
    """ Check that a release on MB has relationships for composers,
    performers, and wikipedia links. """

    @celery.task(base=DunyaReleaseTask, ignore_result=True)
    def task(releasestate_id, releaseid, releasedir):
        pass

def get_musicbrainz_release_for_dir(dirname):
    release_ids = set()
    for fname in os.path.listdir(dirname):
        fpath = os.path.join(dirname, fname)
        meta = compmusic.file_metadata(fpath)
        rel = meta["meta"]["releaseid"]
        if rel:
            release_ids.update(rel)
    return release_ids

@celery.task(ignore_result=True)
def load_musicbrainz_collection(collectionid, root_dir, name):
    """ Load a musicbrainz collection into the database.
    TODO: what if the collectionid doesn't exist
    - Need to log files with no release and 
           release with no files
    """
    releases = compmusic.get_releases_in_collection(collectionid)
    coll = Collection.objects.create(id=collectionid, root_directory=root_dir, name=name)
    collstate = CollectionState.objects.create()
    for relid in releases:
        print "."
        try:
            mbrelease = compmusic.mb.get_release_by_id(relid)["release"]
            title = mbrelease["title"]
            rel = MusicbrainzRelease.objects.create(id=relid, collection=coll, title=title)
        except: # TODO: correct mb error here
            print "missing", relid
            # TODO: log error message

    for root, d, files in os.walk(root_dir):
        if len(files) > 0:
            cd = CollectionDirectory.objects.create(collection=coll, path=d)
            rels = get_musicbrainz_release_for_dir(d)
            if len(rels) > 1:
                pass
            elif len(rels) == 1:
                try:
                    cd.musicbrainz_release = MusicbrainzRelease.objects.get(id=rels[0])
                    cd.save()
                except MusicbrainzRelease.NotFound:
                    pass
            for f in files:
                CollectionFile.objects.create(name=f, directory=cd)
