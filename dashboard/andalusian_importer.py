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

from __future__ import print_function
import compmusic

import andalusian
import andalusian.models
from dashboard import release_importer
from dashboard.log import logger

MEMBER_OF_GROUP = "5be4c609-9afa-4ea0-910b-12ffb71e3821"


class AndalusianReleaseImporter(release_importer.ReleaseImporter):
    _ArtistClass = andalusian.models.Artist
    _ArtistAliasClass = andalusian.models.ArtistAlias
    _OrchestraClass = andalusian.models.Orchestra
    _OrchestraAliasClass = andalusian.models.OrchestraAlias
    _ReleaseClass = andalusian.models.Album
    _RecordingClass = andalusian.models.Recording
    _InstrumentClass = andalusian.models.Instrument
    _WorkClass = andalusian.models.Work
    imported_orchestras = []

    def _link_release_recording(self, release, recording, trackorder, mnum, tnum):
        if not release.recordings.filter(pk=recording.pk).exists():
            andalusian.models.AlbumRecording.objects.create(
                album=release, recording=recording, track=trackorder)

    def _join_recording_and_works(self, recording, works):
        # A andalusian recording can be of many works. Note that because works
        # in musicbrainz are unordered we don't know if this sequence is
        # correct. All of these recordings will need to be manually checked.
        andalusian.models.RecordingWork.objects.filter(recording=recording).delete()
        sequence = 1
        for w in works:
            andalusian.models.RecordingWork.objects.create(work=w, recording=recording, sequence=sequence)
            sequence += 1

    def _get_instrument(self, instname):
        if not instname:
            return None
        instname = instname.lower()
        try:
            return andalusian.models.Instrument.objects.get(name__iexact=instname)
        except andalusian.models.Instrument.DoesNotExist:
            return andalusian.models.Instrument.objects.create(name=instname)

    def _add_recording_performance(self, recordingid, artistid, perf_type, attrs):
        logger.info("  Adding recording performance...")
        artist = self.add_and_get_artist(artistid)

        instr_name = attrs[-1]
        attrs = attrs[:-1]
        is_lead = False
        if "lead" in attrs:
            is_lead = True

        instrument = self._get_instrument(instr_name)
        if instrument:
            recording = andalusian.models.Recording.objects.get(mbid=recordingid)
            perf = andalusian.models.InstrumentPerformance(recording=recording, instrument=instrument, performer=artist, lead=is_lead)
            perf.save()

    def _add_release_performance(self, releaseid, artistid, instrument, is_lead):
        logger.info("  Adding release performance...")
        artist = self.add_and_get_artist(artistid)
        instrument = self._get_instrument(instrument)
        if instrument:
            release = andalusian.models.Album.objects.get(mbid=releaseid)
            # For each recording in the release, see if the relationship
            # already exists. If not, create it.
            for rec in release.recordings.all():
                if not andalusian.models.InstrumentPerformance.objects.filter(
                   recording=rec, instrument=instrument, performer=artist).exists():
                    perf = andalusian.models.InstrumentPerformance(recording=rec, instrument=instrument, performer=artist, lead=is_lead)
                    perf.save()

    def _apply_tags(self, recording, works, tags):
        pass

    def _add_image_to_release(self, release, directories):
        pass

    def _get_orchestra_performances(self, artistrelationlist):
        performances = []
        for perf in artistrelationlist:
            if perf["type"] == "member of band":
                artistid = perf["target"]
                insts = [p.replace("lead ", "") for p in perf.get("attribute-list", [])]
                performances.append((artistid, insts))
        return performances

    def add_and_get_release_artist(self, artistid):
        return self.add_and_get_orchestra(artistid)

    def add_and_get_artist(self, artistid):
        if artistid in self.imported_artists:
            print("Artist already updated in this import. Not doing it again")
            return self._ArtistClass.objects.get(mbid=artistid)
        mbartist = compmusic.mb.get_artist_by_id(artistid, includes=["url-rels", "artist-rels", "aliases"])["artist"]
        artist = self._create_artist_object(self._ArtistClass, self._ArtistAliasClass, mbartist)
        self.imported_artists.append(artistid)
        return artist

    def add_and_get_orchestra(self, orchestraid):
        if orchestraid in self.imported_orchestras:
            print("Orchestra already updated in this import. Not doing it again")
            return self._OrchestraClass.objects.get(mbid=orchestraid)

        mborchestra = compmusic.mb.get_artist_by_id(orchestraid, includes=["url-rels", "artist-rels", "aliases"])["artist"]
        orchestra = self._create_artist_object(self._OrchestraClass, self._OrchestraAliasClass, mborchestra, alias_ref="orchestra")

        orchestra.group_members.clear()
        if mborchestra.get("type") == "Group":
            for artist, instruments in self._get_orchestra_performances(mborchestra.get("artist-relation-list", [])):
                memberartist = self.add_and_get_artist(artist)
                op, _ = andalusian.models.OrchestraPerformer.objects.get_or_create(orchestra=orchestra, performer=memberartist)
                for instrument in instruments:
                    inst = self._get_instrument(instrument)
                    op.instruments.add(inst)

        self.imported_orchestras.append(orchestraid)
        return orchestra
