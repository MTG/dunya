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

import django.utils.timezone

from dashboard.log import logger

import carnatic
import compmusic
import data

from dashboard import external_data

class ReleaseImporter(object):
    def __init__(self, overwrite=False):
        """Create a carnatic importer.
        Arguments:
          overwrite: If we replace everything in the database with new
                     data even if it exists.
        """
        self.overwrite = overwrite
        self.date_import_started = django.utils.timezone.now()

        self.imported_artists = []
        self.imported_releases = []

    def make_mb_source(self, url):
        sn = data.models.SourceName.objects.get(name="MusicBrainz")
        source, created = data.models.Source.objects.get_or_create(source_name=sn, uri=url)
        if not created:
            source.last_updated = django.utils.timezone.now()
            source.save()
        return source

    def make_wikipedia_source(self, url):
        sn = data.models.SourceName.objects.get(name="Wikipedia")
        source, created = data.models.Source.objects.get_or_create(source_name=sn, uri=url)
        if not created:
            source.last_updated = django.utils.timezone.now()
            source.save()
        return source


    def _create_release_object(self, mbrelease):
        concert, created = carnatic.models.Concert.objects.get_or_create(
                mbid=mbid, defaults={"title": rel["title"]})
        if not created:
            if releaseid in self.imported_releases:
                print "Release already updated in this import. Not doing it again"
                return concert
        if created or self.overwrite:
            year = rel.get("date", "")[:4]
            if year:
                year = int(year)
            else:
                year = None
            concert.title = rel["title"]
            concert.year = year
            credit_phrase = rel.get("artist-credit-phrase")
            concert.artistcredit = credit_phrase
            source = self.make_mb_source("http://musicbrainz.org/release/%s" % mbid)
            concert.source = source
            concert.save()

        if not created and self.overwrite:
            # If it already exists and we're doing an overwrite
            concert.artists.clear()
        for a in rel["artist-credit"]:
            if isinstance(a, dict):
                artistid = a["artist"]["id"]
                artist = self.add_and_get_artist(artistid)
                logger.info("  artist: %s" % artist)
                if not concert.artists.filter(pk=artist.pk).exists():
                    logger.info("  - adding to artist list")
                    concert.artists.add(artist)

        return concert

    def _create_release_credits(self, release, credits):
        pass

    def _create_recording(self, release, recording):
        pass

    def import_release(self, releaseid, directories):
        rel = compmusic.mb.get_release_by_id(releaseid, includes=["artists", "recordings", "artist-rels"])
        rel = rel["release"]

        mbid = rel["id"]
        logger.info("Adding release %s" % mbid)

        if mbid in self.imported_releases:
            print "Release already updated in this import. Not doing it again"
            return
        release = self._create_release_object(rel)

        recordings = []
        for medium in rel["medium-list"]:
            for track in medium["track-list"]:
                recordings.append(track["recording"]["id"])

        if not created and self.overwrite:
            concert.tracks.clear()
        trackorder = 1
        for recid in recordings:
            recording = self.add_and_get_recording(recid)
            if not concert.tracks.filter(pk=recording.pk).exists():
                carnatic.models.ConcertRecording.objects.create(
                        concert=concert, recording=recording, track=trackorder)
            trackorder += 1

        if not created and self.overwrite:
            concert.performance.clear()
        for perf in self._get_artist_performances(rel.get("artist-relation-list", [])):
            artistid, instrument, is_lead = perf
            self.add_release_performance(releaseid, artistid, instrument, is_lead)

        external_data.import_concert_image(concert, directories, self.overwrite)

    def _add_and_get_artist_composer(self, ArtistClass, artistid, addgroups=True):
        """
        arguments: ArtistClass: models.Artist or models.Composer
        """
        a = compmusic.mb.get_artist_by_id(artistid, includes=["url-rels", "artist-rels"])["artist"]
        artist, created = ArtistClass.objects.get_or_create(mbid=artistid,
                defaults={"name": a["name"]})

        if not created:
            if artistid in self.imported_artists:
                print "Artist already updated in this import. Not doing it again"
                return artist
        if created or self.overwrite:
            logger.info("  adding artist/composer %s" % (artistid, ))
            source = self.make_mb_source("http://musicbrainz.org/artist/%s" % artistid)
            artist.source = source
            artist.name = a["name"]
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

            # TODO: Annoying hack to only work on artists
            if ArtistClass == carnatic.models.Artist and addgroups:
                if self.overwrite:
                    artist.group_members.clear()
                for member in a.get("artist-relation-list", []):
                    if "member" in member["type"] and member.get("direction") == "backward":
                        memberartist = self._add_and_get_artist_composer(ArtistClass, member["target"])
                        artist.group_members.add(memberartist)

            # add wikipedia references if they exist
            for rel in a.get("url-relation-list", []):
                if rel["type"] == ["wikipedia"]:
                    source = self.make_wikipedia_source(rel["url"])
                    if not artist.references.filter(pk=source.pk).exists():
                        artist.references.add(source)

            external_data.import_artist_bio(artist, self.overwrite)
        return artist

    def add_and_get_artist(self, artistid):
        return self._add_and_get_artist_composer(carnatic.models.Artist, artistid)

    def add_and_get_composer(self, artistid):
        return self._add_and_get_artist_composer(carnatic.models.Composer, artistid)


    def _get_artist_performances(self, artistrelationlist):
        performances = []
        for perf in artistrelationlist:
            if perf["type"] in ["vocal", "instrument"]:
                artistid = perf["target"]
                attrs = perf.get("attribute-list", [])
                is_lead = False
                for a in attrs:
                    if "lead" in a:
                        is_lead = True
                if perf["type"] == "instrument":
                    inst = perf["attribute-list"][0]
                else:
                    inst = "vocal"
                performances.append((artistid, inst, is_lead))
        return performances

    def add_and_get_recording(self, recordingid):
        mbrec = compmusic.mb.get_recording_by_id(recordingid, includes=["tags", "work-rels", "artist-rels"])
        mbrec = mbrec["recording"]

        mbwork = None
        for work in mbrec.get("work-relation-list", []):
            if work["type"] == "performance":
                mbwork = self.add_and_get_work(work["target"], raagas, taalas)
        rec.work = mbwork

        tags = mbrec.get("tag-list", [])

        _create_recording_and_work(mbrec, work, tags)

    def _create_recording_and_works(self, recording, works, tags):
        rec, created = carnatic.models.Recording.objects.get_or_create(mbid=recordingid)

        if created or self.overwrite:
            logger.info("  adding recording %s" % (recordingid,))
            raagas = self._get_raaga(mbrec.get("tag-list", []))
            taalas = self._get_taala(mbrec.get("tag-list", []))
            source = self.make_mb_source("http://musicbrainz.org/recording/%s" % recordingid)
            rec.source = source
            rec.length = mbrec.get("length")
            rec.title = mbrec["title"]
            rec.save()

        if not created and self.overwrite:
            rec.performance.clear()
        for perf in self._get_artist_performances(mbrec.get("artist-relation-list", [])):
            artistid, instrument, is_lead = perf
            self.add_recording_performance(recordingid, artistid, instrument, is_lead)

        return rec

    def add_and_get_work(self, workid, raagas, taalas):
        mbwork = compmusic.mb.get_work_by_id(workid, includes=["artist-rels"])["work"]
        work, created = carnatic.models.Work.objects.get_or_create(mbid=workid,
                defaults={"title": mbwork["title"]})

        if created or self.overwrite:
            source = self.make_mb_source("http://musicbrainz.org/work/%s" % workid)
            work.source = source
            work.title = mbwork["title"]
            work.save()

            if self.overwrite:
                work.raaga.clear()
                work.taala.clear()
                work.composer = None

            for seq, rname in raagas:
                r = self.get_raaga(rname)
                if r:
                    carnatic.models.WorkRaaga.objects.create(work=work, raaga=r, sequence=seq)
                else:
                    logger.warn("Cannot find raaga: %s" % rname)

            for seq, tname in taalas:
                t = self.get_taala(tname)
                if t:
                    carnatic.models.WorkTaala.objects.create(work=work, taala=t, sequence=seq)
                else:
                    logger.warn("Cannot find taala: %s" % tname)

            for artist in mbwork.get("artist-relation-list", []):
                if artist["type"] == "composer":
                    composer = self.add_and_get_composer(artist["target"])
                    work.composer = composer
                    work.save()
                elif artist["type"] == "lyricist":
                    # TODO: Lyricist
                    pass

        return work


    def add_recording_performance(self, recordingid, artistid, instrument, is_lead):
        logger.info("  Adding recording performance...")
        artist = self.add_and_get_artist(artistid)
        instrument = self.get_instrument(instrument)
        if instrument:
            recording = carnatic.models.Recording.objects.get(mbid=recordingid)
            perf = carnatic.models.InstrumentPerformance(recording=recording, instrument=instrument, performer=artist, lead=is_lead)
            perf.save()

    def add_release_performance(self, releaseid, artistid, instrument, is_lead):
        # TODO: Can we de-duplicate this with the recording stuff above
        logger.info("  Adding concert performance...")
        artist = self.add_and_get_artist(artistid)
        instrument = self.get_instrument(instrument)
        if instrument:
            concert = carnatic.models.Concert.objects.get(mbid=releaseid)
            perf = carnatic.models.InstrumentConcertPerformance(concert=concert, instrument=instrument, performer=artist, lead=is_lead)
            perf.save()

    def get_instrument(self, instname):
        try:
            return carnatic.models.Instrument.objects.fuzzy(name=instname)
        except carnatic.models.Instrument.DoesNotExist:
            try:
                alias = carnatic.models.InstrumentAlias.objects.fuzzy(name=instname)
                return alias.instrument
            except carnatic.models.InstrumentAlias.DoesNotExist:
                return None

