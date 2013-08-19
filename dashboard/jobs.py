import celery
import os

from dashboard import models
from dashboard.log import logger

import carnatic
import compmusic
import data

import completeness
import populate_images

@celery.task()
def import_release(releasepk):
    release = models.MusicbrainzRelease.objects.get(pk=releasepk)
    release.start_state()
    ri = ReleaseImporter(release.collection.id)
    ri.import_release(release.mbid)
    release.try_finish_state()
    # Import the data
    # Do release-specific checks
    # Match each file to the recordings in the release
    # -- can be more than 1 directory per release
    # do recording/file-specific checks
    # Import files to docserver

def get_musicbrainz_release_for_dir(dirname):
    """ Get a unique list of all the musicbrainz release IDs that
    are in tags in mp3 files in the given directory.
    """
    release_ids = set()
    for fname in os.listdir(dirname):
        fpath = os.path.join(dirname, fname)
        if compmusic.is_mp3_file(fpath):
            meta = compmusic.file_metadata(fpath)
            rel = meta["meta"]["releaseid"]
            if rel:
                release_ids.add(rel)
    return list(release_ids)

def _get_mp3_files(files):
    """ See if a list of files consists only of mp3 files """
    # TODO: This should be any audio file
    # TODO: replace with util method
    return [f for f in files if os.path.splitext(f)[1].lower() == ".mp3"]

@celery.task(ignore_result=True)
def update_collection(collectionid):
    """ Delete releases that have been removed from the collection
        and add new releases """
    found_releases = compmusic.get_releases_in_collection(collectionid)
    coll = models.Collection.objects.get(pk=collectionid)
    existing_releases = [r.mbid for r in coll.musicbrainzrelease_set.all()]
    to_remove = set(existing_releases) - set(found_releases)
    to_add = set(found_releases) - set(existing_releases)

    for relid in to_add:
        try:
            mbrelease = compmusic.mb.get_release_by_id(relid)["release"]
            title = mbrelease["title"]
            rel, created = models.MusicbrainzRelease.objects.get_or_create(mbid=relid, collection=coll, defaults={"title": title})
        except compmusic.mb.MusicBrainzError:
            coll.add_log_message("The collection had an entry for %s but I can't find a release with that ID" % relid)

    for relid in to_remove:
        coll.musicbrainzrelease_set.filter(mbid=relid).delete()

def _match_directory_to_release(collectionid, root):
    coll = models.Collection.objects.get(pk=collectionid)
    collectionroot = coll.root_directory
    rels = get_musicbrainz_release_for_dir(root)
    print root
    print rels
    print "======="
    if not collectionroot.endswith("/"):
        collectionroot += "/"
    if root.startswith(collectionroot):
        # This should always be true since we scan from the collection root
        shortpath = root[len(collectionroot):]
    cd, created = models.CollectionDirectory.objects.get_or_create(collection=coll, path=shortpath)
    if len(rels) == 1:
        releaseid = rels[0]
        try:
            therelease = models.MusicbrainzRelease.objects.get(mbid=releaseid, collection=coll)
            cd.musicbrainzrelease = models.MusicbrainzRelease.objects.get(mbid=releaseid, collection=coll)
            cd.save()
            cd.add_log_message("Successfully matched to a release", None)

            mp3files = _get_mp3_files(os.listdir(root))
            for f in mp3files:
                cfile, created = models.CollectionFile.objects.get_or_create(name=f, directory=cd)

        except models.MusicbrainzRelease.DoesNotExist:
            cd.add_log_message("Cannot find this directory's release (%s) in the imported releases" % (releaseid, ), None)
    elif len(rels) == 0:
        cd.add_log_message("No releases found in ID3 tags", None)
    else:
        cd.add_log_message("More than one release found in ID3 tags", None)



@celery.task(ignore_result=True)
def scan_and_link(collectionid):
    """ Re-scan the directory for a release. Add & link new directories,
        Remove directories that have been deleted,
        Try and find a match for releases that didn't have a match.
    """

    coll = models.Collection.objects.get(pk=collectionid)
    collectionroot = coll.root_directory
    if not collectionroot.endswith("/"):
        collectionroot += "/"
    found_directories = []
    for root, d, files in os.walk(collectionroot):
        mp3files = _get_mp3_files(files)
        if len(mp3files) > 0:
            found_directories.append(root)
    existing_directories = [c.full_path for c in coll.collectiondirectory_set.all()] 

    to_remove = set(existing_directories) - set(found_directories)
    to_add = set(found_directories) - set(existing_directories)

    print "to_add", to_add
    print "to_remove", to_remove

    for d in to_add:
        _match_directory_to_release(collectionid, d)

    for d in to_remove:
        # We have a full path, but collectiondirectories are
        # stored with a partial path, so cut it.
        shortpath = root[len(collectionroot):]
        coll.collectiondirectory_set.get(path=shortpath).delete()

    # TODO: This is the same code as `rematch_unknown_directory`, deduplicate?
    cds = coll.collectiondirectory_set.filter(musicbrainzrelease__isnull=True)
    for cd in cds:
        print "trying to re-match", cd
        _match_directory_to_release(coll.id, cd.full_path)

@celery.task(ignore_result=True)
def rematch_unknown_directory(directoryid):
    cd = models.CollectionDirectory.objects.get(pk=directoryid)
    _match_directory_to_release(cd.collection.id, cd.full_path)

@celery.task(ignore_result=True)
def load_musicbrainz_collection(collectionid):
    """ Load a musicbrainz collection into the dashboard database.
    """
    coll = models.Collection.objects.get(pk=collectionid)
    coll.set_status_importing()
    releases = compmusic.get_releases_in_collection(collectionid)
    self.update_collection(collectionid)

    self.scan_and_link(collectionid)
