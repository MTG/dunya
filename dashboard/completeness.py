import django.utils.timezone

import celery
import os
import json
import logging
logging.basicConfig(level=logging.INFO)

from dashboard import models

import carnatic
import compmusic
from musicbrainzngs import caa

class CompletenessBase(object):
    """ Base class for a task that checks something is correct """

    # If this checker is for a file (f), or release (r)
    type = None
    # a template to include when talking about results
    templatefile = None
    # If true, abort an import when a task fails
    abort_on_bad = False

    # The task to run.
    # It returns a tuple (status, data) where data is a dict that is
    # stored in the database. Prepare_view knows what to do with the data.
    def task(self, fileid, releaseid):
        pass

    def do_check(self, the_id):
        result, data = self.task(the_id)
        thismodule = "%s.%s" % (self.__class__.__module__, self.__class__.__name__)
        checker = models.CompletenessChecker.objects.get(module=thismodule)
        if self.type == 'f':
            thefile = models.CollectionFile.objects.get(pk=the_id)
            result = 'g' if result else 'b' 
            fs = models.CollectionFileResult.objects.create(collectionfile=thefile, checker=checker, result=result)
            if data:
                fs.data = json.dumps(data)
                fs.save()
        elif self.type == 'r':
            therelease = models.MusicbrainzRelease.objects.get(pk=the_id)
            result = 'g' if result else 'b' 
            rs = models.MusicbrainzReleaseResult.objects.create(musicbrainzrelease=therelease, checker=checker, result=result)
            if data:
                rs.data = json.dumps(data)
                rs.save()
        return result

class MakamTags(CompletenessBase):
    """ Check that the makam and usul tags on this file's
    recording page in musicbrainz have matching entries
    in the local database """
    type = 'f'
    templatefile = 'makam.html'
    name = 'Recording makam and usul'

    def task(self, collectionfile_id):
        thefile = models.CollectionFile.objects.get(pk=collectionfile_id)
        fpath = thefile.path
        meta = compmusic.file_metadata(fpath)
        m = meta["meta"]
        recordingid = m["recordingid"]
        mbrec = compmusic.mb.get_recording_by_id(recordingid, includes=["tags"])
        mbrec = mbrec["recording"]
        tags = mbrec.get("tag-list", [])
        res = {}
        makams = []
        usuls = []
        forms = []
        for t in tags:
            tag = t["name"]
            if compmusic.tags.has_makam(tag):
                makams.append(compmusic.tags.parse_makam(tag))
            if compmusic.tags.has_usul(tag):
                usuls.append(compmusic.tags.parse_usul(tag))
            if compmusic.tags.has_form(tag):
                forms.append(compmusic.tags.parse_form(tag))
        res["recordingid"] = recordingid
        # TODO: Check that the makam/usul/form is in the Makam database

        res["gotmakam"] = len(makams) > 0
        res["gotusul"] = len(usuls) > 0
        res["gotform"] = len(forms) > 0
        res["makam"] = makams
        res["usul"] = usuls
        res["form"] = forms
        if makams and usuls and forms:
            return (True, res)
        else:
            return (False, res)

class RaagaTaalaFile(CompletenessBase):
    """ Check that the raaga and taala tags on this file's
    recording page in musicbrainz have matching entries
    in the local database """
    type = 'f'
    templatefile = 'raagataala.html'
    name = 'Recording raaga and taala'

    def task(self, collectionfile_id):
        thefile = models.CollectionFile.objects.get(pk=collectionfile_id)
        fpath = thefile.path
        meta = compmusic.file_metadata(fpath)
        m = meta["meta"]
        recordingid = m["recordingid"]
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
        res["gottaala"] = len(taalas) > 0
        res["raaga"] = raagas
        res["taala"] = taalas
        if raagas and taalas and not missingt and not missingr:
            return (True, res)
        else:
            return (False, res)


class CoverartFile(CompletenessBase):
    """ Check that a file has embedded coverart """
    type = 'f'
    name = 'File embedded coverart'

    def task(self, collectionfile_id):
        thefile = models.CollectionFile.objects.get(pk=collectionfile_id)
        fpath = thefile.path
        art = compmusic.get_coverart(fpath)
        ret = {}
        return (art is not None, ret)

class ReleaseCoverart(CompletenessBase):
    """ Check that a release has coverart on the CAA """
    type = 'r'
    name = 'Cover art archive coverart'

    def task(self, musicbrainzrelease_id):
        release = models.MusicbrainzRelease.objects.get(pk=musicbrainzrelease_id)
        coverart = caa.get_coverart_list(release.mbid)
        ret = {}
        return (coverart is not None, ret)

class FileTags(CompletenessBase):
    """ Check that a file has musicbrainz tags set.
    This does not check that the musicbrainz tags are valid,
    only that they exist."""
    type = 'f'
    templatefile = 'filetags.html'
    name = 'File tags'

    def task(self, collectionfile_id):
        thefile = models.CollectionFile.objects.get(pk=collectionfile_id)
        fpath = thefile.path
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
    templatefile = 'releaserels.html'


    def parse_recording(self, recordingid):
        logging.info("Recordingid %s" % recordingid)
        recording = compmusic.mb.get_recording_by_id(recordingid, includes=["work-rels", "artist-rels"])
        recording = recording["recording"]
        artistrels = self.get_artist_rels(recording)
        workrels = recording.get("work-relation-list", [])
        works = [w["work"] for w in workrels if w["type"] == "performance"]
        if len(works):
            theworkid = works[0]["id"]
            thework = compmusic.mb.get_work_by_id(theworkid, includes=["artist-rels"])["work"]
            worktitle = thework["title"]
        else:
            theworkid = None
            thework = None
            worktitle = None
        thecomposer = None
        if thework:
            composers = [w["artist"] for w in thework.get("artist-relation-list", []) if w["type"] == "composer"]
            if len(composers):
                thecomposer = composers[0]
        return {"workid": theworkid, "worktitle": worktitle, "composer": thecomposer,\
                "id": recording["id"], "title": recording["title"], "performers": artistrels}


    def get_artist_rels(self, release):
        rels = release.get("artist-relation-list", [])
        ret = []
        for r in rels:
            if r["type"] == "instrument" or r["type"] == "vocal":
                ret.append(r)
        return ret

    def task(self, musicbrainzrelease_id):
        mbrelease = models.MusicbrainzRelease.objects.get(pk=musicbrainzrelease_id)
        includes = ["recordings", "url-rels"]
        release = compmusic.mb.get_release_by_id(mbrelease.mbid, includes=includes)

        release = release["release"]
        recordings = []
        for m in release.get("medium-list", []):
            for rec in m.get("track-list", []):
                recordings.append(self.parse_recording(rec["recording"]["id"]))

        releaserels = self.get_artist_rels(release)

        # Work relationship for each of the recordings
        # [{"id": recordingid, "title": recordingtitle}, ]
        missingworks = []
        for r in recordings:
            if r["workid"] is None:
                missingworks.append({"id": r["id"], "title": r["title"]})

        # Composer relationship for each of the works 
        # [{"id": workid, "title": worktitle}, ]
        missingcomposers = []
        for r in recordings:
            if r["composer"] is None and r["workid"] is not None:
                missingcomposers.append({"id": r["workid"], "title": r["worktitle"]})

        # Performance relationship for the release or the recordings
        # Only populate this if there is no release-level relationships
        # and a recording has no relationships
        # [{"id": recordingid, "title": recordingtitle}, ]
        missingperformers = []
        if not releaserels:
            for r in recordings:
                if not r["performers"]:
                    missingperformers.append({"id": r["id"], "title": r["title"]})
        else:
            print "have release_rels"

        def check_instrument(instrname):
            from carnatic import models
            try:
                models.Instrument.objects.fuzzy(instrname)
                return True
            except models.Instrument.DoesNotExist:
                try:
                    models.InstrumentAlias.objects.fuzzy(instrname)
                    return True
                except models.InstrumentAlias.DoesNotExist:
                    pass
            return False

        # Instrument exists in the DB for each performance
        # We test instruments in the 'release' test, not a separate 'recording'
        # test because sometimes instrument rels are on the release.
        # ["instrumentname", ]
        missinginstruments = set()
        for r in releaserels:
            if len(r["attribute-list"]):
                instrumentname = r["attribute-list"][0]
                if not check_instrument(instrumentname):
                    missinginstruments.add(instrumentname)
        for r in recordings:
            for p in r["performers"]:
                if len(p["attribute-list"]):
                    instrumentname = p["attribute-list"][0]
                    if not check_instrument(instrumentname):
                        missinginstruments.add(instrumentname)

        ret = {"missingworks": missingworks, "missingcomposers": missingcomposers, "missingperfomers": missingperformers, "missinginstruments": list(missinginstruments)}
        val = not (len(missingworks) or len(missingcomposers) or len(missingperformers) or len(missinginstruments))
        return (val, ret)

class CorrectMBID(CompletenessBase):
    """Check that the Musicbrainz IDs in the file tags are correct.
    Do this by performing a search for the release id and hope it's correct.
    Do a really simple tag <-> mb title check to make sure it looks like it's
    the right release.
    Try and match every mb recording id to an id that's in the file listing.
    Return an error if there's an MB recording id with no match, or a
    file recordingid that isn't in MB.
    """
    type = 'r'
    templatefile = 'validmbid.html'
    name = 'MBID validator'
    abort_on_bad = True

    def task(self, musicbrainzrelease_id):
        release = models.MusicbrainzRelease.objects.get(pk=musicbrainzrelease_id)
        mbrelease = compmusic.mb.get_release_by_id(release.mbid, includes=["recordings"])
        mbrelease = mbrelease["release"]

        recordings = {}
        for m in mbrelease.get("medium-list", []):
            for rec in m.get("track-list", []):
                recid = rec["recording"]["id"]
                recordings[recid] = rec["recording"]

        mbrecordings = set(recordings.keys())
        cfiles = release.all_files()
        localrecordings = set([c.recordingid for c in cfiles])
        # Recording IDs on musicbrainz that we don't have in file tags
        unmatchedmb = list(mbrecordings - localrecordings)
        # Recording IDs in file tags that aren't part of this release
        badlocal = list(localrecordings - mbrecordings)

        retdata = {}
        if len(unmatchedmb):
            retdata["unmatchedmb"] = {k: recordings[k] for k in unmatchedmb}
        if len(badlocal):
            retdata["badlocal"] = {}
            for b in badlocal:
                retdata["badlocal"][b] = models.CollectionFile.objects.get(recordingid=b).name

        retval = False if len(unmatchedmb) or len(badlocal) else True
        return (retval, retdata)
