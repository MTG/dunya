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

import compmusic
import data

from dashboard import external_data

RELEASE_TYPE_WIKIPEDIA = "29651736-fa6d-48e4-aadc-a557c6add1cb"
MEMBER_OF_GROUP = "5be4c609-9afa-4ea0-910b-12ffb71e3821"
RELATION_COMPOSER = "d59d99ea-23d4-4a80-b066-edca32ee158f"
RELATION_LYRICIST = "3e48faba-ec01-47fd-8e89-30e81161661c"

class ReleaseImporter(object):
    def __init__(self, overwrite=False, is_bootleg=False, collection=None):
        """Create a release importer.
        Arguments:
          overwrite: If we replace everything in the database with new
                     data even if it exists.
          is_bootleg: If true, mark releases as bootleg
        """
        self.overwrite = overwrite
        self.is_bootleg = is_bootleg
        self.date_import_started = django.utils.timezone.now()
        self.collection = collection

        self.imported_artists = []
        self.imported_composers = []
        self.imported_releases = []

    def _get_year_from_date(self, date):
        if date:
            date = date[:4]
            date = int(date)
        else:
            date = None
        return date

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

    def import_release(self, releaseid, directories):
        if releaseid in self.imported_releases:
            print "Release already updated in this import. Not doing it again"
            return self._ReleaseClass.objects.get(mbid=releaseid)

        rel = compmusic.mb.get_release_by_id(releaseid, includes=["artists", "recordings", "artist-rels", "release-groups"])
        rel = rel["release"]

        mbid = rel["id"]
        logger.info("Adding release %s" % mbid)

        release = self._create_release_object(rel)

        # Create release primary artists
        if self.overwrite:
            # If it already exists and we're doing an overwrite
            release.artists.clear()
        for a in rel["artist-credit"]:
            if isinstance(a, dict):
                artistid = a["artist"]["id"]
                artist = self.add_and_get_release_artist(artistid)
                logger.info("  artist: %s" % artist)
                if not release.artists.filter(pk=artist.pk).exists():
                    logger.info("  - adding to artist list")
                    release.artists.add(artist)

        recordings = []
        for mnum, medium in enumerate(rel["medium-list"], 1):
            for tnum, track in enumerate(medium["track-list"], 1):
                recordings.append( (track["recording"]["id"], mnum, tnum))
        if self.overwrite:
            release.recordings.clear()
        trackorder = 1
        for recid, mnum, tnum in recordings:
            recob = self.add_and_get_recording(recid)
            self._link_release_recording(release, recob, trackorder, mnum, tnum)
            trackorder += 1

        for perf in self._get_artist_performances(rel.get("artist-relation-list", [])):
            artistid, instrument, is_lead = perf
            self._add_release_performance(release.mbid, artistid, instrument, is_lead)

        external_data.import_release_image(release, directories, self.overwrite)
        self.imported_releases.append(releaseid)
        return release

    def _create_release_object(self, mbrelease):
        release, created = self._ReleaseClass.objects.get_or_create(
            mbid=mbrelease["id"], defaults={"title": mbrelease["title"]})
        if created or self.overwrite:
            rel_type = mbrelease["release-group"]
            if "release-group" in mbrelease and "primary-type" in mbrelease["release-group"]:
                release.rel_type = mbrelease["release-group"]["primary-type"]
            if "status" in mbrelease:
                release.status = mbrelease["status"]
            release.title = mbrelease["title"]
            year = self._get_year_from_date(mbrelease.get("date"))
            release.year = year
            credit_phrase = mbrelease.get("artist-credit-phrase")
            release.artistcredit = credit_phrase
            source = self.make_mb_source("http://musicbrainz.org/release/%s" % mbrelease["id"])
            release.source = source
            if self.is_bootleg:
                release.bootleg = True
            release.collection = self.collection
            release.save()

        return release

    def _create_artist_object(self, ArtistKlass, AliasKlass, mbartist, alias_ref="artist"):
        artistid = mbartist["id"]

        artist, created = ArtistKlass.objects.get_or_create(
            mbid=artistid,
            defaults={"name": mbartist["name"]})

        if created or self.overwrite:
            logger.info("  adding artist/composer %s" % (artistid, ))
            source = self.make_mb_source("http://musicbrainz.org/artist/%s" % artistid)
            artist.source = source
            artist.name = mbartist["name"]
            if mbartist.get("type") == "Person":
                artist.artist_type = "P"
            elif mbartist.get("type") == "Group":
                artist.artist_type = "G"
            if mbartist.get("gender") == "Male":
                artist.gender = "M"
            elif mbartist.get("gender") == "Female":
                artist.gender = "F"
            dates = mbartist.get("life-span")
            if dates:
                artist.begin = dates.get("begin")
                artist.end = dates.get("end")
            artist.save()

            # add wikipedia references if they exist
            if self.overwrite:
                artist.references.clear()
            for rel in mbartist.get("url-relation-list", []):
                if rel["type-id"] == RELEASE_TYPE_WIKIPEDIA:
                    source = self.make_wikipedia_source(rel["target"])
                    if not artist.references.filter(pk=source.pk).exists():
                        artist.references.add(source)

            if self.overwrite:
                # We can't 'clear' an alias list from artist because an alias
                # object requires an artist.
                # TODO Deleting these each time we overwrite means we churn the
                # alias ids. This may or may not be a good idea
                args = {}
                args[alias_ref] = artist
                AliasKlass.objects.filter(**args).delete()
            for alias in mbartist.get("alias-list", []):
                a = alias["alias"]
                primary = alias.get("primary")
                locale = alias.get("locale")
                args = {"alias": a}
                args[alias_ref] = artist
                aob, created = AliasKlass.objects.get_or_create(**args)
                if primary:
                    aob.primary = True
                if locale:
                    aob.locale = locale
                aob.save()

            external_data.import_artist_wikipedia(artist, self.overwrite)
        return artist

    def add_and_get_release_artist(self, artistid):
        return self.add_and_get_artist(artistid)

    def add_and_get_artist(self, artistid):
        if artistid in self.imported_artists:
            print "Artist already updated in this import. Not doing it again"
            return self._ArtistClass.objects.get(mbid=artistid)

        mbartist = compmusic.mb.get_artist_by_id(artistid, includes=["url-rels", "artist-rels", "aliases"])["artist"]
        artist = self._create_artist_object(self._ArtistClass, self._ArtistAliasClass, mbartist)

        if self.overwrite:
            artist.group_members.clear()
        if mbartist.get("type") == "Group":
            for member in mbartist.get("artist-relation-list", []):
                if member["type-id"] == MEMBER_OF_GROUP and member.get("direction") == "backward":
                    memberartist = self.add_and_get_artist(member["target"])
                    if not artist.group_members.filter(mbid=memberartist.mbid).exists():
                        artist.group_members.add(memberartist)
        self.imported_artists.append(artistid)
        return artist

    def add_and_get_composer(self, artistid):
        if artistid in self.imported_composers:
            print "Composer already updated in this import. Not doing it again"
            return self._ComposerClass.objects.get(mbid=artistid)

        mbartist = compmusic.mb.get_artist_by_id(artistid, includes=["url-rels", "artist-rels", "aliases"])["artist"]
        composer = self._create_artist_object(self._ComposerClass, self._ComposerAliasClass, mbartist, alias_ref="composer")
        self.imported_composers.append(artistid)
        return composer

    def _get_artist_performances(self, artistrelationlist):
        performances = []
        for perf in artistrelationlist:
            if perf["type"] in ["vocal", "instrument", "performer", "performing orchestra"]:
                artistid = perf["target"]
                attrs = perf.get("attribute-list", [])
                is_lead = False
                for a in attrs:
                    if "lead" in a:
                        is_lead = True
                if perf["type"] == "instrument":
                    # The attributes 'additional' or 'solo' may be set.
                    # If this is the case then remove them so that we don't
                    # select them as the instrument name
                    if "additional" in perf.get("attribute-list", []):
                        perf["attribute-list"].remove("additional")
                    if "solo" in perf.get("attribute-list", []):
                        perf["attribute-list"].remove("solo")
                    if "guest" in perf.get("attribute-list", []):
                        perf["attribute-list"].remove("guest")
                    insts = perf.get("attribute-list", [])
                    # TODO: If someone performed more than 1 instrument
                    # we won't catch it
                    if insts:
                        inst = insts[0]
                    else:
                        inst = None
                elif perf["type"] == "vocal":
                    inst = "vocal"
                else:
                    inst = None
                performances.append((artistid, inst, is_lead))
        return performances

    def add_and_get_recording(self, recordingid):
        mbrec = compmusic.mb.get_recording_by_id(recordingid, includes=["tags", "work-rels", "artist-rels", "artists"])
        mbrec = mbrec["recording"]

        rec, created = self._RecordingClass.objects.get_or_create(mbid=recordingid)
        if created or self.overwrite:
            logger.info("  adding recording %s" % (recordingid,))
            source = self.make_mb_source("http://musicbrainz.org/recording/%s" % recordingid)
            rec.source = source
            rec.length = mbrec.get("length")
            rec.title = mbrec["title"]
            rec.save()

            artistids = []
            # Create recording primary artists
            for a in mbrec.get("artist-credit", []):
                if isinstance(a, dict):
                    artistid = a["artist"]["id"]
                    artistids.append(artistid)
            self._add_recording_artists(rec, artistids)

            works = []
            for work in mbrec.get("work-relation-list", []):
                if work["type"] == "performance":
                    w = self.add_and_get_work(work["target"])
                    works.append(w)

            tags = mbrec.get("tag-list", [])
            # Join recording and works in a subclass because some models
            # have 1 work per recording and others have many
            self._join_recording_and_works(rec, works)

            # Sometime we attach tags to works, sometimes to recordings
            self._apply_tags(rec, works, tags)

            if self.overwrite:
                IPClass = rec.get_object_map("performance")
                IPClass.objects.filter(recording=rec).delete()
            for perf in self._get_artist_performances(mbrec.get("artist-relation-list", [])):
                artistid, instrument, is_lead = perf
                self._add_recording_performance(recordingid, artistid, instrument, is_lead)

        return rec

    def _clear_work_composers(self, work):
        pass
    def _add_recording_artists(self, rec, artistids):
        pass

    def _add_work_attributes(self, work, mbwork, created):
        pass

    def add_and_get_work(self, workid):
        mbwork = compmusic.mb.get_work_by_id(workid, includes=["artist-rels"])["work"]
        work, created = self._WorkClass.objects.get_or_create(
            mbid=workid,
            defaults={"title": mbwork["title"]})

        if created or self.overwrite:
            source = self.make_mb_source("http://musicbrainz.org/work/%s" % workid)
            work.source = source
            work.title = mbwork["title"]
            work.save()

        self._clear_work_composers(work)
        self._add_work_attributes(work, mbwork, created)

        for artist in mbwork.get("artist-relation-list", []):
            if artist["type-id"] == RELATION_COMPOSER:
                composer = self.add_and_get_composer(artist["target"])
                if not work.composers.filter(pk=composer.pk).exists():
                    work.composers.add(composer)
            elif artist["type-id"] == RELATION_LYRICIST:
                lyricist = self.add_and_get_composer(artist["target"])
                if not work.lyricists.filter(pk=lyricist.pk).exists():
                    work.lyricists.add(lyricist)

        return work

class ImportFailedException(Exception):
    pass
