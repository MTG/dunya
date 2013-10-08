import celery
import os

from dashboard.log import logger

import carnatic
import compmusic
import data

from dashboard import external_data

class ReleaseImporter(object):
    def __init__(self, collectionid, directories=[]):
        self.collectionid = collectionid
        self.directories = directories

    def make_mb_source(self, url):
        sn = data.models.SourceName.objects.get(name="MusicBrainz")
        source = data.models.Source.objects.get_or_create(source_name=sn, uri=url)
        return source

    def make_wikipedia_source(self, url):
        sn = data.models.SourceName.objects.get(name="Wikipedia")
        source = data.models.Source.objects.get_or_create(source_name=sn, uri=url)
        return source

    def import_release(self, releaseid):
        # TODO: Can be more than one directory here
        rel = compmusic.mb.get_release_by_id(releaseid, includes=["artists","recordings"])
        rel = rel["release"]

        mbid = rel["id"]
        logger.info("Adding release %s" % mbid)
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
            logger.info("  artist: %s" % artist)
            if not concert.artists.filter(pk=artist.pk).exists():
                logger.info("  - adding to artist list")
                concert.artists.add(artist)
        credit_phrase = rel.get("artist-credit-phrase")
        if credit_phrase:
            concert.artistcredit = credit_phrase
            concert.save()
        recordings = []
        for medium in rel["medium-list"]:
            for track in medium["track-list"]:
                recordings.append(track["recording"]["id"])
        for recid in recordings:
            recording = self.add_and_get_recording(recid)
            concert.tracks.add(recording)

        # TODO: Release hooks
        external_data.import_concert_image(concert, self.directories)

    def add_and_get_artist(self, artistid):
        try:
            artist = carnatic.models.Artist.objects.get(mbid=artistid)
        except carnatic.models.Artist.DoesNotExist:
            logger.info("  adding artist %s" % (artistid, ))
            a = compmusic.mb.get_artist_by_id(artistid, includes=["url-rels"])["artist"]
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
            
            # add wikipedia references if they exist
            for rel in a["url-relation-list"]:
                if rel["type"] == ["wikipedia"]:
                    source = self.make_wikipedia_source(rel["url"])
                    artist.references.add(source)

            # TODO: Artist hooks

            external_data.import_artist_bio(artist.pk)
        return artist

    def _get_raaga(self, taglist):
        ret = []
        seq = 1
        for t in taglist:
            name = t["name"].lower()
            if compmusic.tags.has_raaga(name):
                ret.append( (seq, compmusic.tags.parse_raaga(name)) )
                seq += 1
        return ret

    def _get_taala(self, taglist):
        ret = []
        seq = 1
        for t in taglist:
            name = t["name"].lower()
            if compmusic.tags.has_taala(name):
                ret.append( (seq, compmusic.tags.parse_taala(name)) )
                seq += 1
        return ret

    def add_and_get_recording(self, recordingid):
        try:
            rec = carnatic.models.Recording.objects.get(mbid=recordingid)
        except carnatic.models.Recording.DoesNotExist:
            logger.info("  adding recording %s" % (recordingid,))
            mbrec = compmusic.mb.get_recording_by_id(recordingid, includes=["tags", "work-rels", "artist-rels"])
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
        # TODO: Tests, update status
        return rec

    def add_and_get_work(self, workid, raagas, taalas):
        try:
            w = carnatic.models.Work.objects.get(mbid=workid)
        except carnatic.models.Work.DoesNotExist:
            mbwork = compmusic.mb.get_work_by_id(workid, includes=["artist-rels"])["work"]
            w = carnatic.models.Work(title=mbwork["title"], mbid=workid)
            source = self.make_mb_source("http://musicbrainz.org/work/%s" % workid)
            w.source = source
            w.save()
            for seq, rname in raagas:
                r = self.add_and_get_raaga(rname)
                if r:
                    carnatic.models.WorkRaaga.objects.create(work=w, raaga=r, sequence=seq)
                else:
                    logger.warn("Cannot find raaga: %s" % rname)
            for seq, tname in taalas:
                t = self.add_and_get_taala(tname)
                if t:
                    carnatic.models.WorkTaala.objects.create(work=w, taala=t, sequence=seq)
                else:
                    logger.warn("Cannot find taala: %s" % tname)
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
            logger.info("  adding composer %s" % (artistid, ))
            a = compmusic.mb.get_artist_by_id(artistid)["artist"]
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
        logger.info("  Adding performance...")
        artist = self.add_and_get_artist(artistid)
        instrument = self.add_and_get_instrument(instrument)
        if instrument:
            recording = carnatic.models.Recording.objects.get(mbid=recordingid)
            perf = carnatic.models.InstrumentPerformance(recording=recording, instrument=instrument, performer=artist, lead=is_lead)
            perf.save()

    def add_and_get_instrument(self, instname):
        try:
            return carnatic.models.Instrument.objects.fuzzy(name=instname)
        except carnatic.models.Instrument.DoesNotExist:
            return None


