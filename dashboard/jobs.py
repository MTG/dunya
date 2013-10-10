import celery
import os
import traceback

from dashboard import models
from dashboard.log import logger
from dashboard import release_importer

import carnatic
import compmusic
import data

import docserver
import docserver.util

import completeness
#import populate_images

class DunyaTask(celery.Task):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print "got an exception"
        print einfo
        try:
            theobj = self.ObjectClass.objects.get(pk=args[0])
            theobj.add_log_message(einfo)
            theobj.set_state_error()
        except self.ObjectClass.DoesNotExist:
            classname = "%s.%s" % (self.ObjectClass.__module__, self.ObjectClass.__name__)
            raise Exception("Cannot find %s object with key %s to add error to" % (classname, args[0]))
        raise exc

class CollectionDunyaTask(DunyaTask):
    ObjectClass = models.Collection

class ReleaseDunyaTask(DunyaTask):
    ObjectClass = models.MusicbrainzRelease

def load_and_import_collection(collectionid):
    # Note, use 'immutable subtasks' (.si()) which doesn't pass results from 1 method to the next
    chain = load_musicbrainz_collection.si(collectionid) | import_all_releases.si(collectionid)
    chain.apply_async()

@celery.task(ignore_result=True)
def rematch_unknown_directory(collectiondirectory_id):
    """ Try and match a CollectionDirectory to a release in the collection. """
    cd = models.CollectionDirectory.objects.get(pk=collectiondirectory_id)
    _match_directory_to_release(cd.collection.id, cd.full_path)

@celery.task(base=CollectionDunyaTask)
def load_musicbrainz_collection(collectionid):
    """ Load a musicbrainz collection into the dashboard database
        and scan collection root to match directories to releases.
    """
    coll = models.Collection.objects.get(pk=collectionid)
    coll.set_state_scanning()
    coll.add_log_message("Starting collection scan")

    update_collection(collectionid)
    scan_and_link(collectionid)

    coll.set_state_scanned()
    coll.add_log_message("Collection scan finished")
    return collectionid

@celery.task(base=ReleaseDunyaTask)
def import_release(releasepk):
    """ Import a single release into the database.
    Arguments:
    pk: a models.MusicbrainzRelease object PK
    """
    release = models.MusicbrainzRelease.objects.get(pk=releasepk)
    original_ignore = release.ignore
    release.set_state_importing()
    release.add_log_message("Starting import")
    collection = release.collection

    # 1. Run release checkers
    abort = False
    rcheckers = collection.checkers.filter(type='r')
    for check in rcheckers:
        inst = check.get_instance()
        release.add_log_message("Running release test %s" % inst.name)
        try:
            res = inst.do_check(release.id)
            # If the test fails and abort_on_bad is set then we stop the import
            abort = abort or (not res and inst.abort_on_bad)
        except Exception as e:
            # also stop the import if there's an exception
            abort = True
            tb = traceback.format_exc()
            release.add_log_message(tb)

    cfiles = models.CollectionFile.objects.filter(directory__musicbrainzrelease=release)
    # 2. Run file checkers
    fcheckers = collection.checkers.filter(type='f')
    for cfile in cfiles:
        # 2a. Check file
        for check in fcheckers:
            inst = check.get_instance()
            cfile.add_log_message("Running file test %s" % inst.name)
            try:
                res = inst.do_check(cfile.id)
                abort = abort or (not res and inst.abort_on_bad)
            except Exception as e:
                abort = True
                tb = traceback.format_exc()
                cfile.add_log_message(tb)

    if not abort:
        # If there have been no errors, import to the docserver
        # and to dunya
        for cfile in cfiles:
            # 3a. Import file to docserver
            docserver.util.docserver_add_mp3(collection.id, release.mbid, cfile.path, cfile.recordingid)
            cfile.set_state_finished()

        # 3b. Import release to dunya database
        if collection.do_import:
            # TODO: Choose a different release importer based on each collection
            # All the directories that make up the files in the collection
            dirs = [c.full_path for c in collection.collectiondirectory_set.all()]
            try:
                ri = release_importer.ReleaseImporter(collection.id, dirs)
                ri.import_release(release.mbid)
            except Exception as e:
                abort = True
                tb = traceback.format_exc()
                release.add_log_message(tb)

    if not abort:
        # If the import succeeded, clean up.
        release.add_log_message("Release import finished")
        release.set_state_finished()
        # If the release was ignored and we've successfully imported it, unignore
        if original_ignore:
            release.ignore = False
            release.save()
    else:
        # 3c. If there was an error, set this release as "ignored"
        release.ignore = True
        release.save()
        release.add_log_message("Release import aborted due to failure")
        release.set_state_error()


@celery.task(base=CollectionDunyaTask)
def import_all_releases(collectionid):
    """ Import releases in a collection.
    This will not import releases that are ignored, or have a state of 'finished'
    It will also not import releases that are missing a matching directory.
    """
    collection = models.Collection.objects.get(pk=collectionid)
    collection.set_state_importing()
    releases = collection.musicbrainzrelease_set.filter(ignore=False)
    unstarted = []
    for r in releases:
        matched_paths = r.collectiondirectory_set.all()
        # Only import if it's not finished and has a matched directory
        if r.get_current_state().state != 'f' and len(matched_paths):
            unstarted.append(r)
    for r in unstarted:
        import_release(r.id)
    collection.set_state_finished()

def _get_musicbrainz_release_for_dir(dirname):
    """ Get a unique list of all the musicbrainz release IDs that
    are in tags in mp3 files in the given directory.
    """
    release_ids = set()
    for fname in _get_mp3_files(os.listdir(dirname)):
        fpath = os.path.join(dirname, fname)
        meta = compmusic.file_metadata(fpath)
        rel = meta["meta"]["releaseid"]
        if rel:
            release_ids.add(rel)
    return list(release_ids)

def _get_mp3_files(files):
    """ Take a list of files and return only the mp3 files """
    # TODO: This should be any audio file, replace with util method
    return [f for f in files if os.path.splitext(f)[1].lower() == ".mp3"]

def update_collection(collectionid):
    """ Sync the contents of a collection on musicbrainz.org to our local
        database.

        If new releases have been added, put them in our local database.
        If releases have been removed, remove referenes to them in our
        database.
    """
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
        except compmusic.mb.ResponseError:
            coll.add_log_message("The collection had an entry for %s but I can't find a release with that ID" % relid)

    for relid in to_remove:
        coll.musicbrainzrelease_set.filter(mbid=relid).delete()

def _match_directory_to_release(collectionid, root):
    """ Try and match a single directory containing audio files to a release
        that exists in the given collection.

        collectionid: the ID of the collection we want the directory to be in
        root: the root path of the directory containing audio files
    """
    coll = models.Collection.objects.get(pk=collectionid)
    collectionroot = coll.root_directory
    print root
    print "======="
    # Remove the path to the collection from the path to the files (we only store relative paths)
    if not collectionroot.endswith("/"):
        collectionroot += "/"
    if root.startswith(collectionroot):
        # This should always be true since we scan from the collection root
        shortpath = root[len(collectionroot):]
    else:
        shortpath = root
    # Try and find the musicbrainz release for the files in the directory
    cd, created = models.CollectionDirectory.objects.get_or_create(collection=coll, path=shortpath)
    rels = _get_musicbrainz_release_for_dir(root)
    if len(rels) == 1:
        releaseid = rels[0]
        try:
            therelease = models.MusicbrainzRelease.objects.get(mbid=releaseid, collection=coll)
            cd.musicbrainzrelease = therelease
            cd.save()
            cd.add_log_message("Successfully matched to a release", None)

            mp3files = _get_mp3_files(os.listdir(root))
            for f in mp3files:
                meta = compmusic.file_metadata(os.path.join(root, f))
                recordingid = meta["meta"].get("recordingid")
                cfile, created = models.CollectionFile.objects.get_or_create(name=f, directory=cd, recordingid=recordingid)

        except models.MusicbrainzRelease.DoesNotExist:
            cd.add_log_message("Cannot find this directory's release (%s) in the imported releases" % (releaseid, ), None)
    elif len(rels) == 0:
        cd.add_log_message("No releases found in ID3 tags", None)
    else:
        cd.add_log_message("More than one release found in ID3 tags", None)

def scan_and_link(collectionid):
    """ Scan the root directory of a collection and see if any directories
    have been added or removed.

    If they've been removed, delete references to them. If they've been
    added, scan the files for a musicbrainz release id and match them
    to musicbrainz releases that are part of the collection.
    """

    coll = models.Collection.objects.get(pk=collectionid)
    collectionroot = coll.root_directory
    if not collectionroot.endswith("/"):
        collectionroot += "/"
    if isinstance(collectionroot, str):
        # Pass a unicode string to os.walk and it returns directories as unicode
        collectionroot = collectionroot.decode("utf-8")
    found_directories = []
    for root, d, files in os.walk(collectionroot):
        mp3files = _get_mp3_files(files)
        if len(mp3files) > 0:
            found_directories.append(root)
    existing_directories = [c.full_path for c in coll.collectiondirectory_set.all()] 

    to_remove = set(existing_directories) - set(found_directories)
    to_add = set(found_directories) - set(existing_directories)

    for d in to_add:
        _match_directory_to_release(collectionid, d)

    for d in to_remove:
        # We have a full path, but collectiondirectories are
        # stored with a partial path, so cut it.
        shortpath = d[len(collectionroot):]
        coll.collectiondirectory_set.get(path=shortpath).delete()

    # For every CollectionDirectory that isn't matched to a MusicbrainzRelease,
    # try and match it
    cds = coll.collectiondirectory_set.filter(musicbrainzrelease__isnull=True)
    for cd in cds:
        _match_directory_to_release(coll.id, cd.full_path)

