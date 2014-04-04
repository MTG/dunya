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
from dashboard import release_importer

import makam
import data

class MakamReleaseImporter(release_importer.ReleaseImporter):
    _ArtistClass = makam.models.Artist
    _ArtistAliasClass = makam.models.ArtistAlias
    _ComposerClass = makam.models.Composer
    _ComposerAliasClass = makam.models.ComposerAlias
    _ReleaseClass = makam.models.Release
    _RecordingClass = makam.models.Recording
    _InstrumentClass = makam.models.Instrument

    def _link_release_recording(self, concert, recording, trackorder):
        if not concert.tracks.filter(pk=recording.pk).exists():
            makam.models.ReleaseRecording.objects.create(
                    concert=concert, recording=recording, track=trackorder)


    def _join_recording_and_works(self, recording, works):
        # A makam recording can have many works
        sequence = 1
        for w in works:
            makam.models.RecordingWork.objects.create(work=w, recording=recording, sequence=sequence)
            sequence += 1

    def _apply_tags(self, recording, works, tags):
        # `tags` includes tags for the recording. But we should also look
        # for tags in the work and add them
        pass

    def get_instrument(self, instname):
        try:
            return makam.models.Instrument.objects.get(name=instname)
        except makam.models.Instrument.DoesNotExist:
            try:
                alias = makam.models.InstrumentAlias.objects.get(name=instname)
                return alias.instrument
            except makam.models.InstrumentAlias.DoesNotExist:
                return None


    def _add_recording_performance(self, recordingid, artistid, instrument, is_lead):
        logger.info("  Adding recording performance...")
        artist = self.add_and_get_artist(artistid)
        instrument = self.get_instrument(instrument)
        if instrument:
            recording = makam.models.Recording.objects.get(mbid=recordingid)
            perf = makam.models.InstrumentPerformance(recording=recording, instrument=instrument, performer=artist, lead=is_lead)
            perf.save()

    def _clear_release_performances(self, release):
        release.performance.clear()

    def _add_release_performance(self, releaseid, artistid, instrument, is_lead):
        logger.info("  Adding concert performance...")
        artist = self.add_and_get_artist(artistid)
        instrument = self.get_instrument(instrument)
        if instrument:
            concert = makam.models.Concert.objects.get(mbid=releaseid)
            perf = makam.models.InstrumentConcertPerformance(concert=concert, instrument=instrument, performer=artist, lead=is_lead)
            perf.save()
