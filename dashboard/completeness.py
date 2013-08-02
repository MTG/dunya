import django.utils.timezone

import celery
import os
import json

from dashboard import models
import carnatic
import compmusic
from musicbrainzngs import caa

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

    def _finish_release(releasestatus_id):
        rs = models.ReleaseStatus.objects.get(pk=releasestatus_id)
        if isinstance(retval, bool):
            retval, data = (retval, {})
        else:
            retval, data = retval
        status = 'g' if retval else 'b' 
        rs.status = status
        rs.data = json.dumps(data)
        rs.datetime = django.utils.timezone.now()
        rs.save()

        rs.release.try_finish_state()

    def _finish_file(filestatus_id):
        fs = models.FileStatus.objects.get(pk=filestatus_id)
        if isinstance(retval, bool):
            retval, data = (retval, {})
        else:
            retval, data = retval
        status = 'g' if retval else 'b' 
        fs.status = status
        fs.data = json.dumps(data)
        fs.datetime = django.utils.timezone.now()
        fs.save()

        fs.file.try_finish_state()

class RaagaTaalaFile(CompletenessBase):
    """ Check that the raaga and taala tags on this file's
    recording page in musicbrainz have matching entries
    in the local database """
    type = 'f'
    templatestub = 'raagataala.html'
    name = 'Recording raaga and taala'

    def task(filestatus_id):
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


class CoverartFile(CompletenessBase):
    """ Check that a file has embedded coverart """
    type = 'f'
    name = 'File embedded coverart'

    def task(filestatus_id):
        fs = models.FileStatus.objects.get(pk=filestatus_id)
        fpath = fs.file.path
        art = compmusic.get_coverart(fpath)
        ret = {}
        return (art is not None, ret)

class ReleaseCoverart(CompletenessBase):
    """ Check that a release has coverart on the CAA """
    type = 'r'
    name = 'Cover art archive coverart'

    def task(releasestatus_id):
        rs = models.ReleaseStatus.objects.get(pk=releasestatus_id)
        release = rs.release
        mbid = release.id
        coverart = caa.get_coverart_list(mbid)
        ret = {}
        return (coverart is not None, ret)

class FileTags(CompletenessBase):
    """ Check that a file has all the correct musicbrainz tags """
    type = 'f'
    templatestub = 'filetags.html'
    name = 'File tags'

    def task(filestatus_id):
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


class ReleaseRelationships(CompletenessBase):
    """ Check that a release on MB has relationships for composers,
    performers, and wikipedia links. """
    type = 'r'
    name = 'Release relationships'

    def task(self, releasestate_id, releaseid, releasedir):
        pass
