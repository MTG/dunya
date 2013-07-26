import celery
import os

from dashboard import models
import carnatic
import compmusic

import completeness

@celery.task()
def import_release(releaseid, directory):
    ri = ReleaseImporter(releaseid, directory)
    ri.import_release()

class ReleaseImporter(object):
    def __init__(self, releaseid, directory):
        self.releaseid = releaseid
        self.directory = directory

    def import_release(self):
        rel = mb.get_release_by_id(self.releaseid, includes=["artists","recordings"])
        rel = rel["release"]

        mbid = rel["id"]
        logging.info("Adding release %s" % mbid)
        try:
            concert = carnatic.models.Concert.objects.get(mbid=mbid)
        except carnatic.models.Concert.DoesNotExist:
            year = rel.get("date", "")[:4]
            if year:
                year = int(year)
            else:
                year = None
            concert = carnatic.models.Concert(mbid=mbid, title=rel["title"], year=year)
            source = self.make_mb_source("http://musicbrainz.org/release/%s" % mbid)
            concert.source = source
            concert.save()
            for a in rel["artist-credit"]:
                artistid = a["artist"]["id"]
                artist = self.add_and_get_artist(artistid)
                logging.info("  artist: %s" % artist)
                concert.artists.add(artist)
        recordings = []
        for medium in rel["medium-list"]:
            for track in medium["track-list"]:
                recordings.append(track["recording"]["id"])
        for recid in recordings:
            recording = self.add_and_get_recording(recid)
            concert.tracks.add(recording)

        # TODO: Release hooks
        # TODO: Post-import:
        # Match files in a directory to the recordings
        # Add files to the docserver


    def add_and_get_artist(self, artistid):
        try:
            artist = carnatic.models.Artist.objects.get(mbid=artistid)
        except carnatic.models.Artist.DoesNotExist:
            logging.info("  adding artist %s" % (artistid, ))
            a = mb.get_artist_by_id(artistid)["artist"]
            artist = carnatic.models.Artist(name=a["name"], mbid=artistid)
            source = self.make_mb_source("http://musicbrainz.org/artist/%s" % artistid)
            artist.source = source
            if a.get("type") == "Person":
                artist.artist_type = "P"
            elif a.get("type") == "Group":
                artist.artist_type = "G"
            if a.get("gender") == "Male":
                artist.gender = "M"
            elif a.get("gender") == "Female":
                artist.gender = "F"
            dates = a.get("life-span")
            if dates:
                artist.begin = dates.get("begin")
                artist.end = dates.get("end")
            artist.save()
            # TODO: Artist hooks
            compmusic.populate_images.import_artist(artist)
        return artist

    def _get_raaga(self, taglist):
        ret = []
        for t in taglist:
            name = t["name"].lower()
            if compmusic.parse_tags.has_raaga(name):
                ret.append(compmusic.parse_tags.parse_raaga(name))
        return ret

    def _get_taala(self, taglist):
        ret = []
        for t in taglist:
            name = t["name"].lower()
            if compmusic.parse_tags.has_taala(name):
                ret.append(compmusic.parse_tags.parse_taala(name))
        return ret

    def add_and_get_recording(self, recordingid):
        try:
            rec = carnatic.models.Recording.objects.get(mbid=recordingid)
        except carnatic.models.Recording.DoesNotExist:
            logging.info("  adding recording %s" % (recordingid,))
            mbrec = mb.get_recording_by_id(recordingid, includes=["tags", "work-rels", "artist-rels"])
            mbrec = mbrec["recording"]
            raagas = self._get_raaga(mbrec.get("tag-list", []))
            taalas = self._get_taala(mbrec.get("tag-list", []))
            mbwork = None
            for work in mbrec.get("work-relation-list", []):
                if work["type"] == "performance":
                    mbwork = self.add_and_get_work(work["target"], raagas, taalas)
            rec = carnatic.models.Recording(mbid=recordingid, work=mbwork)
            source = self.make_mb_source("http://musicbrainz.org/recording/%s" % recordingid)
            rec.source = source
            rec.length = mbrec.get("length")
            rec.title = mbrec["title"]
            rec.save()
            for perf in mbrec.get("artist-relation-list", []):
                if perf["type"] == "vocal":
                    artistid = perf["target"]
                    is_lead = "lead" in perf["attribute-list"]
                    self.add_performance(recordingid, artistid, "vocal", is_lead)
                elif perf["type"] == "instrument":
                    artistid = perf["target"]
                    attrs = perf.get("atrribute-list", [])
                    is_lead = False
                    if "lead" in attrs:
                        is_lead = "True"
                        attrs.remove("lead")
                    inst = perf["attribute-list"][0]
                    self.add_performance(recordingid, artistid, inst, is_lead)

        # TODO: Recording hooks
        return rec

    def add_and_get_work(self, workid, raagas, taalas):
        try:
            w = carnatic.models.Work.objects.get(mbid=workid)
        except carnatic.models.Work.DoesNotExist:
            mbwork = mb.get_work_by_id(workid, includes=["artist-rels"])["work"]
            w = carnatic.models.Work(title=mbwork["title"], mbid=workid)
            source = self.make_mb_source("http://musicbrainz.org/work/%s" % workid)
            w.source = source
            w.save()
            for seq, rname in raagas:
                r = self.add_and_get_raaga(rname)
                if r:
                    carnatic.models.WorkRaaga.objects.create(work=w, raaga=r, sequence=seq)
                else:
                    logging.warn("Cannot find raaga: %s" % rname)
            for seq, tname in taalas:
                t = self.add_and_get_taala(tname)
                if t:
                    carnatic.models.WorkTaala.objects.create(work=w, taala=t, sequence=seq)
                else:
                    logging.warn("Cannot find taala: %s" % tname)
            for artist in mbwork.get("artist-relation-list", []):
                if artist["type"] == "composer":
                    composer = self.add_and_get_composer(artist["target"])
                    w.composer = composer
                    w.save()
                elif artist["type"] == "lyricist":
                    pass
        return w

    def add_and_get_composer(self, artistid):
        # TODO: Can we make this generic with artist? 
        # (just model type is different?)
        try:
            composer = carnatic.models.Composer.objects.get(mbid=artistid)
        except carnatic.models.Composer.DoesNotExist:
            logging.info("  adding composer %s" % (artistid, ))
            a = mb.get_artist_by_id(artistid)["artist"]
            composer = carnatic.models.Composer(name=a["name"], mbid=artistid)
            source = self.make_mb_source("http://musicbrainz.org/artist/%s" % artistid)
            composer.source = source
            if a.get("gender") == "Male":
                composer.gender = "M"
            elif a.get("gender") == "Female":
                composer.gender = "F"
            dates = a.get("life-span")
            if dates:
                composer.begin = dates.get("begin")
                composer.end = dates.get("end")
            composer.save()

        # TODO: Artist hooks

        return composer

    def add_and_get_raaga(self, raaganame):
        try:
            return carnatic.models.Raaga.objects.fuzzy(name=raaganame)
        except carnatic.models.Raaga.DoesNotExist, e:
            try:
                alias = carnatic.models.RaagaAlias.objects.fuzzy(name=raaganame)
                return alias.raaga
            except carnatic.models.RaagaAlias.DoesNotExist, e:
                return None

    def add_and_get_taala(self, taalaname):
        try:
            return carnatic.models.Taala.objects.fuzzy(name=taalaname)
        except carnatic.models.Taala.DoesNotExist, e:
            try:
                alias = carnatic.models.TaalaAlias.objects.fuzzy(name=taalaname)
                return alias.taala
            except carnatic.models.TaalaAlias.DoesNotExist, e:
                return None

    def add_performance(self, recordingid, artistid, instrument, is_lead):
        logging.info("  Adding performance...")
        artist = self.add_and_get_artist(artistid)
        instrument = self.add_and_get_instrument(instrument)
        recording = carnatic.models.Recording.objects.get(mbid=recordingid)
        perf = carnatic.models.InstrumentPerformance(recording=recording, instrument=instrument, performer=artist, lead=is_lead)
        perf.save()

    def add_and_get_instrument(self, instname):
        return carnatic.models.Instrument.objects.fuzzy(name=instname)

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
    existing_releases = [r.id for r in coll.musicbrainzrelease_set.all()]
    to_remove = set(existing_releases) - set(found_releases)
    to_add = set(found_releases) - set(existing_releases)

    for relid in to_add:
        try:
            mbrelease = compmusic.mb.get_release_by_id(relid)["release"]
            title = mbrelease["title"]
            rel, created = models.MusicbrainzRelease.objects.get_or_create(id=relid, collection=coll, defaults={"title": title})
        except compmusic.mb.MusicBrainzError:
            coll.add_log_message("The collection had an entry for %s but I can't find a release with that ID" % relid)

    for relid in to_remove:
        models.MusicbrainzRelease.objects.get(id=relid).delete()

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
            cd.musicbrainzrelease = models.MusicbrainzRelease.objects.get(id=releaseid)
            cd.save()

            mp3files = _get_mp3_files(os.listdir(root))
            for f in mp3files:
                cfile, created = models.CollectionFile.objects.get_or_create(name=f, directory=cd)

        except models.MusicbrainzRelease.DoesNotExist:
            cd.add_log_message(None, "Cannot find this release (%s) in the imported releases" % (theid, ))
    elif len(rels) == 0:
        cd.add_log_message(None, "No releases found in ID3 tags")
    else:
        cd.add_log_message(None, "More than one release found in ID3 tags")



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

    for d in to_add:
        _match_directory_to_release(collectionid, d)

    for d in to_remove:
        # We have a full path, but collectiondirectories are
        # stored with a partial path, so cut it.
        shortpath = root[len(collectionroot):]
        coll.collectiondirectory_set.get(path=shortpath).delete()

@celery.task(ignore_result=True)
def load_musicbrainz_collection(collectionid):
    """ Load a musicbrainz collection into the dashboard database.
    """
    coll = models.Collection.objects.get(pk=collectionid)
    coll.set_status_importing()
    releases = compmusic.get_releases_in_collection(collectionid)
    self.update_collection(collectionid)

    self.scan_and_link(collectionid)
