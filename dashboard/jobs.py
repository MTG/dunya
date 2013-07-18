from django.db import transaction
import celery
import os
import json
import datetime

from dashboard import models
import carnatic
import compmusic
from musicbrainzngs import caa

class DunyaStatusFileTask(celery.Task):
    """ A celery task that performs a health check on a file """
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        if status == "SUCCESS":
            filestatus_id = args[0]
            fs = models.FileStatus.objects.get(pk=filestatus_id)
            if isinstance(retval, bool):
                retval, data = (retval, {})
            else:
                retval, data = retval
            status = 'g' if retval else 'b' 
            fs.status = status
            fs.data = json.dumps(data)
            fs.datetime = datetime.datetime.now()
            fs.save()

            fs.file.try_finish_state()

class DunyaStatusReleaseTask(celery.Task):
    """ A celery task that performs a health check on a directory
    representing a release """
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        if status == "SUCCESS":
            releasestatus_id = args[0]
            rs = models.ReleaseStatus.objects.get(pk=releasestatus_id)
            if isinstance(retval, bool):
                retval, data = (retval, {})
            else:
                retval, data = retval
            status = 'g' if retval else 'b' 
            rs.status = status
            rs.data = json.dumps(data)
            rs.datetime = datetime.datetime.now()
            rs.save()

            rs.release.try_finish_state()

class CompletenessBase(object):
    """ Base class for a task that checks something is correct """

    # If this checker is for a file (f), or release (r)
    type = None
    # a template to include when talking about results
    templatestub = None

    # a view stub that is called with data that the checker task
    # saves. It returns a dict that is passed to the templatestub file.
    def prepare_view(self, data):
        """ Default prepare_view just passes the data through """
        return data

    # the celery task to run.
    # It returns a boolean indicating the status of the check (True=good)
    # or a tuple (status, data) where data is a dict that is stored
    # in the database. Prepare_view knows what to do with the data
    def task(fileid, releaseid):
        pass

@celery.task(base=DunyaStatusFileTask)
def raagataalafiletask(filestatus_id):
    fs = models.FileStatus.objects.get(pk=filestatus_id)
    fpath = fs.file.path
    meta = compmusic.file_metadata(fpath)
    m = meta["meta"]
    recordingid = m["recordingid"]
    print "http://musicbrainz.org/recording/%s" % recordingid
    mbrec = compmusic.mb.get_recording_by_id(recordingid, includes=["tags"])
    mbrec = mbrec["recording"]
    tags = mbrec.get("tag-list", [])
    res = {}
    raagas = []
    taalas = []
    for t in tags:
        tag = t["name"]
        if compmusic.tags.has_raaga(tag):
            raagas.append(compmusic.tags.parse_raaga(tag))
        if compmusic.tags.has_taala(tag):
            taalas.append(compmusic.tags.parse_taala(tag))
    res["recordingid"] = recordingid
    missingr = []
    missingt = []
    for r in raagas:
        try:
            carnatic.models.Raaga.objects.fuzzy(r)
        except carnatic.models.Raaga.DoesNotExist:
            missingr.append(r)
        if missingr:
            res["missingr"] = missingr
    for t in taalas:
        try:
            carnatic.models.Taala.objects.fuzzy(t)
        except carnatic.models.Taala.DoesNotExist:
            missingt.append(t)
        if missingt:
            res["missingt"] = missingt
            
    res["gotraaga"] = len(raagas) > 0
    res["gottaala"] = len(taalas) > 1
    if raagas and taalas and not missingt and not missingr:
        return (True, res)
    else:
        return (False, res)

class RaagaTaalaFile(CompletenessBase):
    """ Check that the raaga and taala tags on this file's
    recording page in musicbrainz have matching entries
    in the local database """
    type = 'f'
    templatestub = 'raagataala.html'
    name = 'Recording raaga and taala'
    task = raagataalafiletask

@celery.task(base=DunyaStatusFileTask)
def coverartfiletask(filestatus_id):
    fs = models.FileStatus.objects.get(pk=filestatus_id)
    fpath = fs.file.path
    art = compmusic.get_coverart(fpath)
    ret = {}
    return (art is not None, ret)

class CoverartFile(CompletenessBase):
    """ Check that a file has embedded coverart """
    type = 'f'
    name = 'File embedded coverart'
    task = coverartfiletask


@celery.task(base=DunyaStatusReleaseTask, ignore_result=True)
def releasecoverarttask(releasestatus_id):
    rs = models.ReleaseStatus.objects.get(pk=releasestatus_id)
    release = rs.release
    mbid = release.id
    coverart = caa.get_coverart_list(mbid)
    ret = {}
    return (coverart is not None, ret)

class ReleaseCoverart(CompletenessBase):
    """ Check that a release has coverart on the CAA """
    type = 'r'
    name = 'Cover art archive coverart'
    task = releasecoverarttask

@celery.task(base=DunyaStatusFileTask)
def filetagstask(filestatus_id):
    fs = models.FileStatus.objects.get(pk=filestatus_id)
    fpath = fs.file.path
    meta = compmusic.file_metadata(fpath)
    complete = True
    data = {}
    m = meta["meta"]
    data.update(m)
    if not m["artist"]:
        complete = False
        data["artist_missing"] = True
    if not m["title"]:
        complete = False
        data["title_missing"] = True
    if not m["release"]:
        complete = False
        data["release_missing"] = True
    if not m["artistid"]:
        complete = False
        data["artistid_missing"] = True
    if not m["releaseid"]:
        complete = False
        data["releaseid_missing"] = True
    if not m["recordingid"]:
        complete = False
        data["recordingid_missing"] = True

    return (complete, data)

class FileTags(CompletenessBase):
    """ Check that a file has all the correct musicbrainz tags """
    type = 'f'
    templatestub = 'filetags.html'
    name = 'File tags'

class ReleaseRelationships(CompletenessBase):
    """ Check that a release on MB has relationships for composers,
    performers, and wikipedia links. """
    type = 'r'
    name = 'Release relationships'

    @celery.task(base=DunyaStatusReleaseTask, ignore_result=True)
    def task(self, releasestate_id, releaseid, releasedir):
        pass

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

def is_mp3_dir(files):
    """ See if a list of files consists only of mp3 files """
    # TODO: This should be any audio file
    # TODO: replace with util method
    extensions = set([os.path.splitext(f)[1].lower() for f in files])
    return ".mp3" in extensions

@celery.task(ignore_result=True)
def load_musicbrainz_collection(collectionid):
    """ Load a musicbrainz collection into the dashboard database.
    """
    coll = models.Collection.objects.get(pk=collectionid)
    coll.status_importing()
    releases = compmusic.get_releases_in_collection(collectionid)
    for relid in releases:
        try:
            mbrelease = compmusic.mb.get_release_by_id(relid)["release"]
            title = mbrelease["title"]
            rel, created = models.MusicbrainzRelease.objects.get_or_create(id=relid, collection=coll, defaults={"title": title})
            for checker in coll.checkers.filter(type='r'):
                models.ReleaseStatus.objects.get_or_create(release=rel, checker=checker)
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
                # This should always be true since we scan from the collection root
                shortpath = root[len(collectionroot):]
            cd, created = models.CollectionDirectory.objects.get_or_create(collection=coll, path=shortpath)
            if len(rels) == 1:
                try:
                    theid = rels[0]
                    cd.musicbrainz_release = models.MusicbrainzRelease.objects.get(id=theid)
                    cd.save()

                    for f in files:
                        if f.lower().endswith(".mp3"):
                            cfile, created = models.CollectionFile.objects.get_or_create(name=f, directory=cd)

                            for checker in coll.checkers.filter(type='f'):
                                models.FileStatus.objects.get_or_create(file=cfile, checker=checker)
                except models.MusicbrainzRelease.DoesNotExist:
                    cd.add_log_message(None, "Cannot find this release (%s) in the Musicbrainz collection" % (theid, ))
            elif len(rels) == 0:
                cd.add_log_message(None, "No releases found in ID3 tags")
            else:
                cd.add_log_message(None, "More than one release found in ID3 tags")

