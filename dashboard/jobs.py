# Copyright 2013,2014 Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of Dunya
#
# Dunya is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation (FSF), either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/


import os
import traceback

import celery
import compmusic
import magic

import data
import docserver
import docserver.util
from dashboard import (
    andalusian_importer,
    carnatic_importer,
    hindustani_importer,
    jingju_importer,
    makam_importer,
    models,
)
from dashboard.log import import_logger
from dunya.celery import app


class DunyaTask(celery.Task):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print("got an exception")
        print(einfo)
        try:
            theobj = self.get_object(args[0])
            theobj.add_log_message(einfo)
            theobj.set_state_error()
        except self.ObjectClass.DoesNotExist:
            classname = f"{self.ObjectClass.__module__}.{self.ObjectClass.__name__}"
            raise Exception(f"Cannot find {classname} object with key {args[0]} to add error to")
        raise exc


class CollectionDunyaTask(DunyaTask):
    ObjectClass = models.Collection

    def get_object(self, key):
        return self.ObjectClass.objects.get(collectionid=key)


class ReleaseDunyaTask(DunyaTask):
    ObjectClass = models.MusicbrainzRelease

    def get_object(self, key):
        return self.ObjectClass.objects.get(pk=key)


def force_load_and_import_collection(collectionid):
    """Scan the collection contents and import every release again
    (including ones already imported)
    """
    # Note, use 'immutable subtasks' (.si()) which doesn't pass results from 1 method to the next
    chain = load_musicbrainz_collection.si(collectionid) | force_import_all_releases.si(collectionid)
    chain.apply_async()


@app.task(ignore_result=True)
def rematch_unknown_directory(collectiondirectory_id):
    """Try and match a CollectionDirectory to a release in the collection."""
    cd = models.CollectionDirectory.objects.get(pk=collectiondirectory_id)
    _match_directory_to_release(cd.collection.collectionid, cd.full_path)


@app.task(base=CollectionDunyaTask)
def load_musicbrainz_collection(collectionid):
    """Load a musicbrainz collection into the dashboard database
    and scan collection root to match directories to releases.
    """
    coll = models.Collection.objects.get(collectionid=collectionid)
    coll.set_state_scanning()
    coll.add_log_message("Starting collection scan")

    update_collection(collectionid)
    scan_and_link(collectionid)

    coll.set_state_scanned()
    coll.add_log_message("Collection scan finished")
    return collectionid


@app.task(base=ReleaseDunyaTask)
def import_single_release(releasepk):
    """A job to find a release's collection, create a release importer,
    and then call import_release
    """
    release = models.MusicbrainzRelease.objects.get(pk=releasepk)
    collection = release.collection

    ri = get_release_importer(collection)
    if not ri:
        release.add_log_message(
            "Cannot discover importer based on collection name (does it include carnatic/hindustani/makam/andalusian?)"
        )
        release.set_state_error()
        return
    import_release(releasepk, ri)


def import_release(releasepk, ri):
    """Import a single release into the database.
    Arguments:
    releasepk: a models.MusicbrainzRelease object PK
    ri: a release_importer object specific to this collection
    """
    release = models.MusicbrainzRelease.objects.get(pk=releasepk)
    original_ignore = release.ignore
    release.set_state_importing()
    release.add_log_message("Starting import")
    collection = release.collection

    # If there have been no errors, import to the docserver
    # and to dunya
    cfiles = models.CollectionFile.objects.filter(directory__musicbrainzrelease=release)
    for cfile in cfiles:
        # 3a. Import file to docserver
        docserver.util.docserver_add_mp3(collection.collectionid, release.mbid, cfile.path, cfile.recordingid)
        cfile.set_state_finished()

    # 3b. Import release to dunya database
    abort = False
    if collection.do_import:
        try:
            directories = [
                os.path.join(collection.audio_directory, d.path) for d in release.collectiondirectory_set.all()
            ]
            # Set the release logger releaseid to the id of the current release
            import_logger.releaseid = release.pk
            ri.import_release(release.mbid, directories)
        except Exception:
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


def get_release_importer(collection):
    name = collection.name.lower()
    name = name.lower()
    data_coll = data.models.Collection.objects.get(collectionid=collection.collectionid)
    ri = None
    if "hindustani" in name:
        ri = hindustani_importer.HindustaniReleaseImporter(data_coll)
    elif "carnatic" in name:
        ri = carnatic_importer.CarnaticReleaseImporter(data_coll)
    elif "makam" in name:
        ri = makam_importer.MakamReleaseImporter(data_coll)
    elif "andalusian" in name:
        ri = andalusian_importer.AndalusianReleaseImporter(data_coll)
    elif "jingju" in name:
        ri = jingju_importer.JingjuReleaseImporter(data_coll)
    return ri


@app.task(base=CollectionDunyaTask)
def force_import_all_releases(collectionid):
    """Reimport releases in a dashboard collection.
    This will (re)import all releases that are in the collection, even if they
    are marked as ignored or are finished, unless they are missing a directory
    """
    collection = models.Collection.objects.get(collectionid=collectionid)
    ri = get_release_importer(collection)
    if not ri:
        collection.add_log_message(
            "Cannot discover importer based on collection name (does it include carnatic/hindustani/makam/andalusian?)"
        )
        collection.set_state_error()
        return
    collection.set_state_importing()
    # unlike the non-force version, we select all releases, not
    # only ones that haven't been ignored
    releases = collection.musicbrainzrelease_set.all()
    unstarted = []
    for r in releases:
        matched_paths = r.collectiondirectory_set.all()
        if len(matched_paths):
            if r.ignore:
                r.ignore = False
                r.save()
            unstarted.append(r)
    for r in unstarted:
        import_release(r.id, ri)
    collection.set_state_finished()


def _get_musicbrainz_release_for_dir(dirname):
    """Get a unique list of all the musicbrainz release IDs that
    are in tags in mp3 files in the given directory.
    """
    release_ids = set()
    for fname in _get_mp3_files(dirname, os.listdir(dirname)):
        fpath = os.path.join(dirname, fname)
        meta = compmusic.file_metadata(fpath)
        if meta:
            rel = meta["meta"]["releaseid"]
            if rel:
                release_ids.add(rel)
    return list(release_ids)


def _get_mp3_files(root_dir, files):
    """Take a list of files and return only the mp3 files"""
    # TODO: This should be any audio file, replace with util method

    ret = []
    for f in files:
        full_path = os.path.join(root_dir, f)
        if os.path.isfile(full_path) and magic.from_file(full_path, mime=True) == "audio/mpeg":
            ret.append(f)
    return ret


def update_collection(collectionid):
    """Sync the contents of a collection on musicbrainz.org to our local
    database.

    If new releases have been added, put them in our local database.
    If releases have been removed, remove referenes to them in our
    database.
    """
    found_releases = compmusic.get_releases_in_collection(collectionid)
    coll = models.Collection.objects.get(collectionid=collectionid)
    existing_releases = [str(r.mbid) for r in coll.musicbrainzrelease_set.all()]
    to_remove = set(existing_releases) - set(found_releases)
    to_add = set(found_releases) - set(existing_releases)

    for relid in to_add:
        try:
            mbrelease = compmusic.mb.get_release_by_id(relid, includes=["artists"])["release"]
            title = mbrelease["title"]
            artist = mbrelease["artist-credit-phrase"]
            rel, created = models.MusicbrainzRelease.objects.get_or_create(
                mbid=relid, collection=coll, defaults={"title": title, "artist": artist}
            )
        except compmusic.mb.ResponseError:
            coll.add_log_message(f"The collection had an entry for {relid} but I can't find a release with that ID")

    for relid in to_remove:
        coll.musicbrainzrelease_set.filter(mbid=relid).delete()


def _match_directory_to_release(collectionid, root):
    """Try and match a single directory containing audio files to a release
    that exists in the given collection.

    collectionid: the ID of the collection we want the directory to be in
    root: the root path of the directory containing audio files
    """
    coll = models.Collection.objects.get(collectionid=collectionid)
    collectionroot = coll.audio_directory
    # Remove the path to the collection from the path to the files (we only store relative paths)
    if not collectionroot.endswith("/"):
        collectionroot += "/"
    if root.startswith(collectionroot):
        # This should always be true since we scan from the collection root
        shortpath = root[len(collectionroot) :]
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
            mp3files = _get_mp3_files(root, os.listdir(root))
            for f in mp3files:
                _create_collectionfile(cd, f)
        except models.MusicbrainzRelease.DoesNotExist:
            pass


def _create_collectionfile(cd, name):
    """arguments:
    cd: a collectiondirectory
    name: the name of the file, with no path information
    """
    path = os.path.join(cd.full_path, name)
    meta = compmusic.file_metadata(path)
    recordingid = meta["meta"].get("recordingid")
    size = os.path.getsize(path)
    cfile, created = models.CollectionFile.objects.get_or_create(
        name=name, directory=cd, recordingid=recordingid, defaults={"filesize": size}
    )
    if not created:
        cfile.filesize = size
        cfile.save()


def scan_and_link(collectionid):
    """Scan the root directory of a collection and see if any directories
    have been added or removed.

    If they've been removed, delete references to them. If they've been
    added, scan the files for a musicbrainz release id and match them
    to musicbrainz releases that are part of the collection.
    """

    coll = models.Collection.objects.get(collectionid=collectionid)
    collectionroot = coll.audio_directory
    if not collectionroot.endswith("/"):
        collectionroot += "/"
    found_directories = []
    for root, _dirs, files in os.walk(collectionroot):
        mp3files = _get_mp3_files(root, files)
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
        shortpath = d[len(collectionroot) :]
        coll.collectiondirectory_set.get(path=shortpath).delete()

    # For every CollectionDirectory that isn't matched to a MusicbrainzRelease,
    # try and match it
    cds = coll.collectiondirectory_set.filter(musicbrainzrelease__isnull=True)
    for cd in cds:
        _match_directory_to_release(coll.collectionid, cd.full_path)

    _check_existing_directories(coll)


def _check_existing_directories(coll):
    # For all of the matched directories, look at the contents of them and
    # remove/add files as needed
    # We don't remove from the docserver because it's not very important to
    # remove them, and it's complex to cover all cases. We do this separately
    for cd in coll.collectiondirectory_set.all():
        files = os.listdir(cd.full_path)
        mp3files = _get_mp3_files(cd.full_path, files)
        existing_f = cd.collectionfile_set.all()
        existing_names = [f.name for f in existing_f]

        to_remove = set(existing_names) - set(mp3files)
        to_add = set(mp3files) - set(existing_names)
        same_files = set(mp3files) & set(existing_names)

        for rm in to_remove:
            # If it was renamed, we will make a CollectionFile in
            # the to_add block below
            cd.collectionfile_set.get(name=rm).delete()

        for f in same_files:
            # Look through all files and see if the mbid has changed. If it's changed,
            # update the reference
            fileobject = cd.collectionfile_set.get(name=f)
            meta = compmusic.file_metadata(os.path.join(cd.full_path, f))
            recordingid = meta["meta"].get("recordingid")
            if recordingid != fileobject.recordingid:
                fileobject.recordingid = recordingid
                fileobject.save()

        if to_add:
            # If there are new files in the directory, just run _match again and
            # it will create the new file objects
            _match_directory_to_release(coll.collectionid, cd.full_path)


@app.task
def delete_collection(collectionpk):
    collection = models.Collection.objects.get(pk=collectionpk)
    collection.delete()
