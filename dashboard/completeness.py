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

    def _get_tags_from_list(self, tags):
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
        return makams, usuls, forms

    def task(self, collectionfile_id):
        thefile = models.CollectionFile.objects.get(pk=collectionfile_id)
        fpath = thefile.path
        meta = compmusic.file_metadata(fpath)
        m = meta["meta"]
        recordingid = m["recordingid"]
        mbrec = compmusic.mb.get_recording_by_id(recordingid, 
                includes=["tags", "work-rels"])["recording"]
        tags = mbrec.get("tag-list", [])
        res = {}
        m, u, f = self._get_tags_from_list(tags)
        res["makams"] = m[:]
        res["usuls"] = u[:]
        res["forms"] = f[:]
        works = mbrec.get("work-relation-list", [])

        # If there's a work, get its id and the id of its composer
        # Also scan for makam/usul tags here too
        for w in works:
            if w["type"] == "performance":
                wid = w["work"]["id"]
                mbwork = compmusic.mb.get_work_by_id(wid, includes=["tags"])["work"]
                tags = mbwork.get("tag-list", [])
                m, u, f = self._get_tags_from_list(tags)
                res["makams"].extend(m)
                res["usuls"].extend(u)
                res["forms"].extend(f)

        # de-duplicate the lists
        res["makams"] = list(set(res["makams"]))
        res["usuls"] = list(set(res["usuls"]))
        res["forms"] = list(set(res["forms"]))

        res["recordingid"] = recordingid
        # TODO: Check that the makam/usul/form is in our list of wanted ones

        res["gotmakam"] = len(res["makams"]) > 0
        res["gotusul"] = len(res["usuls"]) > 0
        res["gotform"] = len(res["forms"]) > 0
        if res["makams"] and res["usuls"] and res["forms"]:
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
        """ Get all works that make up this recording, including id, title, composer.
        Also get the IDs of artists and lead artists
        """
        logging.info("Recordingid %s" % recordingid)
        recording = compmusic.mb.get_recording_by_id(recordingid, includes=["work-rels", "artist-rels"])
        recording = recording["recording"]

        artists, leadartists = self.get_artist_performances(recording.get("artist-relation-list", []))

        workrels = recording.get("work-relation-list", [])
        works = [w["work"] for w in workrels if w["type"] == "performance"]
        retworks = []
        for w in works:
            workid = w["id"]
            mbwork = compmusic.mb.get_work_by_id(workid, includes=["artist-rels"])["work"]
            thework = {"id": w["id"], "title": w["title"], "composers": []}
            composers = [r["artist"] for r in mbwork.get("artist-relation-list", []) if r["type"] == "composer"]
            thework["composers"] = composers
            retworks.append(thework)

        return {"id": recording["id"], "title": recording["title"], \
                "works": retworks, "artists": artists, "leadartists": leadartists}

    def get_artist_performances(self, relationlist):
        leadartists = []
        artists = []
        for arel in relationlist:
            if arel["type"] in ["vocal", "instrument", "performer"]:
                aid = arel["target"]
                attrs = arel.get("attribute-list", [])
                lead = False
                for a in attrs:
                    if "lead" in a:
                        lead = True
                if lead:
                    leadartists.append(arel)
                else:
                    artists.append(arel)
        return artists, leadartists

    def task(self, musicbrainzrelease_id):
        mbrelease = models.MusicbrainzRelease.objects.get(pk=musicbrainzrelease_id)
        includes = ["recordings", "url-rels", "artist-rels", "artists"]
        release = compmusic.mb.get_release_by_id(mbrelease.mbid, includes=includes)
        release = release["release"]

        artists = set()
        for a in release.get("artist-credit", []):
            if isinstance(a, dict):
                artists.add(a)

        recordings = []
        for m in release.get("medium-list", []):
            for rec in m.get("track-list", []):
                recordings.append(self.parse_recording(rec["recording"]["id"]))

        relartists, relleadartists = self.get_artist_performances(release.get("artist-relation-list", []))

        # Missing a work relationship for each of the recordings
        # [{"id": recordingid, "title": recordingtitle}, ]
        missingworks = []
        for r in recordings:
            if len(r["works"]) == 0:
                missingworks.append({"id": r["id"], "title": r["title"]})

        # Missing a composer relationship for each of the works 
        # [{"id": workid, "title": worktitle}, ]
        missingcomposers = []
        for r in recordings:
            for w in r["works"]:
                if len(w["composers"]) == 0:
                    missingcomposers.append({"id": w["id"], "title": w["title"]})

        # Performance relationship for the release or the recordings
        # Only populate this if there is no release-level relationships
        # and a recording has no relationships
        # [{"id": recordingid, "title": recordingtitle}, ]
        missingperformers = []
        if relartists or relleadartists:
            # If the release has some artists set, we're fine
            pass
        else:
            # Otherwise check that all recordings have either an artist or 
            # a lead artist
            for r in recordings:
                if not r["artists"] and not r["leadartists"]:
                    missingperformers.append({"id": r["id"], "title": r["title"]})

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
        for r in relartists:
            if r["type"] == "instrument" and r.get("attribute-list"):
                instrumentname = r["attribute-list"][0]
                if not check_instrument(instrumentname):
                    missinginstruments.add(instrumentname)
        for r in relleadartists:
            if r["type"] == "instrument" and r.get("attribute-list"):
                instrumentname = r["attribute-list"][0]
                if not check_instrument(instrumentname):
                    missinginstruments.add(instrumentname)
        for rec in recordings:
            for r in rec["artists"]:
                if r["type"] == "instrument" and r.get("attribute-list"):
                    instrumentname = r["attribute-list"][0]
                    if not check_instrument(instrumentname):
                        missinginstruments.add(instrumentname)
            for r in rec["leadartists"]:
                if r["type"] == "instrument" and r.get("attribute-list"):
                    instrumentname = r["attribute-list"][0]
                    if not check_instrument(instrumentname):
                        missinginstruments.add(instrumentname)

        ret = {
                "missingworks": missingworks,
                "missingcomposers": missingcomposers,
                "missingperfomers": missingperformers,
                "missinginstruments": list(missinginstruments),
                "releaseartistrels": relartists,
                "releaseleadartistrels": relleadartists,
                "recordings": recordings,
                "artists": list(artists)
                }
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
