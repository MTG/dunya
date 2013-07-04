from django.db import transaction
import celery
import os

from dashboard import models
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

class RaagaTaalaFile(CompletenessBase):
    """ Check that the raaga and taala tags on this file's
    recording page in musicbrainz have matching entries
    in the local database """
    type = 'f'
    templatestub = 'raagataala.html'

    def prepare_view(data):
        pass

    @celery.task(base=DunyaStatusFileTask, ignore_result=True)
    def task(collectionfile_id):
        fg = CollectionFile.objects.get(pk=collectionfile_id)

class CoverartFile(CompletenessBase):
    """ Check that a file has embedded coverart """
    type = 'f'

    @celery.task(base=DunyaStatusFileTask, ignore_result=True)
    def task(collectionfile_id):
        fg = CollectionFile.objects.get(pk=collectionfile_id)

class CoverartRelease(CompletenessBase):
    """ Check that a release has coverart on the CAA """
    type = 'r'

    @celery.task(base=DunyaStatusReleaseTask, ignore_result=True)
    def task(releasestate_id, releaseid, releasedir):
        pass

class FileTags(CompletenessBase):
    """ Check that a file has all the correct musicbrainz tags """
    type = 'f'

    @celery.task(base=DunyaStatusFileTask, ignore_result=True)
    def task(filestate_id, fname):
        pass

class ReleaseRelationships(CompletenessBase):
    """ Check that a release on MB has relationships for composers,
    performers, and wikipedia links. """
    type = 'r'

    @celery.task(base=DunyaStatusReleaseTask, ignore_result=True)
    def task(releasestate_id, releaseid, releasedir):
        pass

def get_musicbrainz_release_for_dir(dirname):
    release_ids = set()
    for fname in os.listdir(dirname):
        fpath = os.path.join(dirname, fname)
        if compmusic.is_mp3_file(fpath):
            meta = compmusic.file_metadata(fpath)
            rel = meta["meta"]["releaseid"]
            if rel:
                print "releaseid", rel
                release_ids.add(rel)
    return release_ids

def is_mp3_dir(files):
    """ See if a list of files consists only of mp3 files """
    # TODO: This should be any audio file
    extensions = set([os.path.splitext(f)[1].lower() for f in files])
    return ".mp3" in extensions

@celery.task(ignore_result=True)
def load_musicbrainz_collection(collectionid):
    """ Load a musicbrainz collection into the database.
    """
    releases = compmusic.get_releases_in_collection(collectionid)
    coll = models.Collection.objects.get(pk=collectionid)
    for relid in releases:
        try:
            mbrelease = compmusic.mb.get_release_by_id(relid)["release"]
            title = mbrelease["title"]
            models.MusicbrainzRelease.objects.get_or_create(id=relid, collection=coll, defaults={"title": title})
        except compmusic.mb.MusicBrainzError:
            coll.add_log_message("The collection had an entry for %s but I can't find a release with that ID" % relid)

    collectionroot = coll.root_directory
    for root, d, files in os.walk(collectionroot):
        if len(files) > 0 and is_mp3_dir(files):
            rels = get_musicbrainz_release_for_dir(root)
            print root
            print rels
            print "======="
            if not collectionroot.endswith("/"):
                collectionroot += "/"
            if root.startswith(collectionroot):
                # This should always be the case, since we'll scan from the
                # collection root
                shortpath = root[len(collectionroot):]
            cd, created = models.CollectionDirectory.objects.get_or_create(collection=coll, path=shortpath)
            if len(rels) == 1:
                try:
                    theid = list(rels)[0]
                    cd.musicbrainz_release = models.MusicbrainzRelease.objects.get(id=theid)
                    cd.save()

                    for f in files:
                        if f.lower().endswith(".mp3"):
                            models.CollectionFile.objects.get_or_create(name=f, directory=cd)
                except models.MusicbrainzRelease.DoesNotExist:
                    cd.add_log_message(None, "there's a release but I don't know what it is")
                    print "cannot find release in the collection"
            else:
                cd.add_log_message(None, "Not one release per folder?")

