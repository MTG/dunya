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
import carnatic
import data

import compmusic

class CarnaticReleaseImporter(release_importer.ReleaseImporter):
    _ArtistClass = carnatic.models.Artist
    _ArtistAliasClass = carnatic.models.ArtistAlias
    _ComposerClass = carnatic.models.Composer
    _ComposerAliasClass = carnatic.models.ComposerAlias
    _ReleaseClass = carnatic.models.Concert
    _RecordingClass = carnatic.models.Recording
    _InstrumentClass = carnatic.models.Instrument
    _WorkClass = carnatic.models.Work

    def _link_release_recording(self, concert, recording, trackorder):
        if not concert.tracks.filter(pk=recording.pk).exists():
            carnatic.models.ConcertRecording.objects.create(
                    concert=concert, recording=recording, track=trackorder)


    def _join_recording_and_works(self, recording, works):
        # A carnatic recording only has one work.
        if len(works):
            w = works[0]
            recording.work = w
            recording.save()

    def _apply_tags(self, recording, works, tags):
        if len(works):
            w = works[0]
            if self.overwrite:
                w.raaga.clear()
                w.taala.clear()

            raagas = self._get_raaga_tags(tags)
            taalas = self._get_taala_tags(tags)

            for seq, rname in raagas:
                r = self._get_raaga(rname)
                if r:
                    carnatic.models.WorkRaaga.objects.create(work=w, raaga=r, sequence=seq)
                else:
                    logger.warn("Cannot find raaga: %s" % rname)

            for seq, tname in taalas:
                t = self._get_taala(tname)
                if t:
                    carnatic.models.WorkTaala.objects.create(work=w, taala=t, sequence=seq)
                else:
                    logger.warn("Cannot find taala: %s" % tname)
        else:
            # If we have no works, we don't need to do this
            return


    def _get_raaga_tags(self, taglist):
        ret = []
        seq = 1
        for t in taglist:
            name = t["name"].lower()
            if compmusic.tags.has_raaga(name):
                ret.append( (seq, compmusic.tags.parse_raaga(name)) )
                seq += 1
        return ret

    def _get_taala_tags(self, taglist):
        ret = []
        seq = 1
        for t in taglist:
            name = t["name"].lower()
            if compmusic.tags.has_taala(name):
                ret.append( (seq, compmusic.tags.parse_taala(name)) )
                seq += 1
        return ret

    def _get_raaga(self, raaganame):
        try:
            return carnatic.models.Raaga.objects.fuzzy(name=raaganame)
        except carnatic.models.Raaga.DoesNotExist, e:
            try:
                alias = carnatic.models.RaagaAlias.objects.fuzzy(name=raaganame)
                return alias.raaga
            except carnatic.models.RaagaAlias.DoesNotExist, e:
                return None

    def _get_taala(self, taalaname):
        try:
            return carnatic.models.Taala.objects.fuzzy(name=taalaname)
        except carnatic.models.Taala.DoesNotExist, e:
            try:
                alias = carnatic.models.TaalaAlias.objects.fuzzy(name=taalaname)
                return alias.taala
            except carnatic.models.TaalaAlias.DoesNotExist, e:
                return None

    def get_instrument(self, instname):
        try:
            return carnatic.models.Instrument.objects.fuzzy(name=instname)
        except carnatic.models.Instrument.DoesNotExist:
            try:
                alias = carnatic.models.InstrumentAlias.objects.fuzzy(name=instname)
                return alias.instrument
            except carnatic.models.InstrumentAlias.DoesNotExist:
                return None


    def _add_recording_performance(self, recordingid, artistid, instrument, is_lead):
        logger.info("  Adding recording performance...")
        artist = self.add_and_get_artist(artistid)
        instrument = self.get_instrument(instrument)
        if instrument:
            recording = carnatic.models.Recording.objects.get(mbid=recordingid)
            perf = carnatic.models.InstrumentPerformance(recording=recording, instrument=instrument, performer=artist, lead=is_lead)
            perf.save()

    def _clear_release_performances(self, release):
        release.performance.clear()

    def _add_release_performance(self, releaseid, artistid, instrument, is_lead):
        logger.info("  Adding concert performance...")
        artist = self.add_and_get_artist(artistid)
        instrument = self.get_instrument(instrument)
        if instrument:
            concert = carnatic.models.Concert.objects.get(mbid=releaseid)
            perf = carnatic.models.InstrumentConcertPerformance(concert=concert, instrument=instrument, performer=artist, lead=is_lead)
            perf.save()
