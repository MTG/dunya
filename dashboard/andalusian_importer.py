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

WORK_WORK_BASED_ON = "6bb1df6b-57f3-434d-8a39-5dc363d2eb78"
WORK_URL_SCORE = "0cc8527e-ea40-40dd-b144-3b7588e759bf"
RECORDING_URL_DOWNLOAD_FOR_FREE = "45d0cbc5-d65b-4e77-bdfd-8a75207cb5c5"


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
            raise release_importer.ImportFailedException("Instrument {} not found".format(instname))

    def _get_works_and_score(self, work_mbids):
        works = []
        for wid in work_mbids:
            works.append(compmusic.mb.get_work_by_id(wid, includes=["work-rels", "url-rels"])["work"])

        # TODO: We just assume that the presence of a "url-relation-list" means that this work has a score
        #       attached to it. It could check the relation type id
        score_works = [w for w in works if "url-relation-list" in w]
        normal_works = [w for w in works if "url-relation-list" not in w]

        # These are works related to the recording. There may be more than 1 'based on' work, but at least
        # one of them must be the score_work_id

        # If the recording has no regular works, return the score
        if len(score_works)==1 and len(normal_works) == 0:
            return score_works[ 0],[]
        # If the recording has no score, return the regular works (may be empty)
        elif len(score_works) == 0:
            return None, normal_works

        # If there is a score work and at least 1 regular work, make sure that the score work is based on
        # each of the regular works
        score_work_id = score_works[0]["id"]
        ok_work_rel = False
        for w in normal_works:
            for work_rel in w.get("work-relation-list", []):
                if work_rel["type-id"] == WORK_WORK_BASED_ON and work_rel["target"] == score_work_id:
                    ok_work_rel = True
        assert ok_work_rel is True

        return score_works[0], normal_works

    def _add_works_from_relations(self, work_rel_list):
        # test
        # In andalusian, some works only exist to link to the score. We only want to add the other works

        work_ids = [w["target"] for w in work_rel_list if w["type-id"] == release_importer.RELATION_RECORDING_WORK_PERFORMANCE]
        score_work, works = self._get_works_and_score(work_ids)
        imported_works = []
        for work in works:
            w = self.add_and_get_work(work["id"])
            imported_works.append(w)
        return imported_works

    def _add_recording_additional_data(self, recordingid, recording):
        # Andalusian importer needs to import audio download url (recording-url relation)
        # and score url (recording-work-url relation)

        mbrec = compmusic.mb.get_recording_by_id(recordingid, includes=["work-rels", "url-rels"])
        mbrec = mbrec["recording"]

        recording_changed = False
        url_rels = [rel for rel in mbrec.get("url-relation-list", []) if rel["type-id"] == RECORDING_URL_DOWNLOAD_FOR_FREE]
        if len(url_rels) == 1:
            url = url_rels[0]["target"]
            recording.archive_url = url
            recording_changed = True

        work_rels = mbrec.get("work-relation-list", [])
        work_ids = [w["target"] for w in work_rels if w["type-id"] == release_importer.RELATION_RECORDING_WORK_PERFORMANCE]
        score_work, works = self._get_works_and_score(work_ids)
        if score_work:
            url_rels = [rel for rel in score_work["url-relation-list"] if rel["type-id"] == WORK_URL_SCORE]
            url = url_rels[0]["target"]
            recording.musescore_url = url
            recording_changed = True

        if recording_changed:
            recording.save()

    def _add_recording_performance(self, recordingid, artistid, perf_type, attrs):
        logger.info("  Adding recording performance...")
        artist = self.add_and_get_artist(artistid)

        # We don't expect to see these two relations here, as we know that all releases in MusicBrainz
        # for this collection have recording-level relationships.
        if perf_type in [release_importer.RELATION_RELEASE_VOCAL, release_importer.RELATION_RELEASE_INSTRUMENT]:
            raise release_importer.ImportFailedException("Found a release-level artist instrument relation on "
                                                         "recording {} which isn't supported".format(recordingid))

        is_lead = False
        instr_name = attrs[-1]
        if perf_type == release_importer.RELATION_RECORDING_VOCAL:
            instr_name = "voice"
            if "lead vocals" in attrs:
                is_lead = True
        elif perf_type == release_importer.RELATION_RECORDING_INSTRUMENT:
            instr_name = attrs[-1]
            attrs = attrs[:-1]
            if "lead" in attrs:
                is_lead = True

        instrument = self._get_instrument(instr_name)
        if instrument:
            recording = andalusian.models.Recording.objects.get(mbid=recordingid)
            perf = andalusian.models.InstrumentPerformance(recording=recording, instrument=instrument, performer=artist, lead=is_lead)
            perf.save()

    def _add_release_performance(self, releasembid, artistid, perf_type, attrs):
        # release.mbid, artistid, perf_type, attrs
        logger.info("  Adding release performance...")

        release = andalusian.models.Album.objects.get(mbid=releasembid)
        for rec in release.recordings.all():
            self._add_recording_performance(rec.mbid, artistid, perf_type, attrs)

    def _apply_tags(self, recording, works, tags):
        pass

    def _add_image_to_release(self, release, directories):
        pass

    def _get_orchestra_performances(self, artistrelationlist):
        # TODO: this shares some logic with _add_recording_performance to rename vocals -> voice.
        performances = []
        for perf in artistrelationlist:
            if perf["type"] == "member of band":
                artistid = perf["target"]
                insts = []
                for instrument in perf.get("attribute-list", []):
                    if instrument in ["lead vocals", "vocals"]:
                        instrument = "voice"
                    insts.append(instrument)
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
