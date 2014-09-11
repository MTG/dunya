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

from dashboard.log import logger
from dashboard import release_importer
import carnatic.models

import compmusic
from compmusic import mb

def remove_deleted_items():
    """ Search musicbrainz for all items in the database and if they
    have been deleted then remove them """

    logger.info("Scanning works...")
    for w in carnatic.models.Work.objects.all():
        try:
            mb.get_work_by_id(w.mbid)
        except mb.ResponseError:
            logger.info("work %s (%s) missing; deleting" % (w, w.mbid))
            w.delete()

    logger.info("Scanning recordings...")
    for r in carnatic.models.Recording.objects.all():
        try:
            mb.get_recording_by_id(r.mbid)
        except mb.ResponseError:
            logger.info("recording %s (%s) missing; deleting" % (r, r.mbid))
            r.delete()

    logger.info("Scanning concerts...")
    for c in carnatic.models.Concert.objects.all():
        try:
            mb.get_release_by_id(c.mbid)
        except mb.ResponseError:
            logger.info("release %s (%s) missing; deleting" % (c, c.mbid))
            c.delete()

    logger.info("Scanning artists...")
    for a in carnatic.models.Artist.objects.all():
        try:
            mb.get_artist_by_id(a.mbid)
        except mb.ResponseError:
            # We import dummy artists to be gurus, leave them here
            if not a.dummy:
                logger.info("artist %s (%s) missing; deleting" % (a, a.mbid))
                a.delete()

    logger.info("Scanning composers...")
    for a in carnatic.models.Composer.objects.all():
        try:
            mb.get_artist_by_id(a.mbid)
        except mb.ResponseError:
            logger.info("artist %s (%s) missing; deleting" % (a, a.mbid))
            a.delete()

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
        if not concert.recordings.filter(pk=recording.pk).exists():
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
                ret.append((seq, compmusic.tags.parse_raaga(name)))
                seq += 1
        return ret

    def _get_taala_tags(self, taglist):
        ret = []
        seq = 1
        for t in taglist:
            name = t["name"].lower()
            if compmusic.tags.has_taala(name):
                ret.append((seq, compmusic.tags.parse_taala(name)))
                seq += 1
        return ret

    def _get_raaga(self, raaganame):
        try:
            return carnatic.models.Raaga.objects.fuzzy(raaganame)
        except carnatic.models.Raaga.DoesNotExist:
            return None

    def _get_taala(self, taalaname):
        try:
            return carnatic.models.Taala.objects.fuzzy(taalaname)
        except carnatic.models.Taala.DoesNotExist:
            return None

    def _get_instrument(self, instname):
        try:
            return carnatic.models.Instrument.objects.fuzzy(instname)
        except carnatic.models.Instrument.DoesNotExist:
            return None

    def _add_recording_performance(self, recordingid, artistid, instrument, is_lead):
        logger.info("  Adding recording performance...")
        artist = self.add_and_get_artist(artistid)
        instrument = self._get_instrument(instrument)
        if instrument:
            recording = carnatic.models.Recording.objects.get(mbid=recordingid)
            perf = carnatic.models.InstrumentPerformance(recording=recording, instrument=instrument, artist=artist, lead=is_lead)
            perf.save()

    def _add_release_performance(self, releaseid, artistid, instrument, is_lead):
        logger.info("  Adding concert performance...")
        artist = self.add_and_get_artist(artistid)
        instrument = self._get_instrument(instrument)

        concert = carnatic.models.Concert.objects.get(mbid=releaseid)
        # Instrument could be None if we don't know it

        for rec in concert.recordings.all():
            if not carnatic.models.InstrumentPerformance.objects.filter(
               recording=rec, instrument=instrument, artist=artist).exists():
                perf = carnatic.models.InstrumentPerformance(recording=rec, instrument=instrument, artist=artist, lead=is_lead)
                perf.save()
    
    def _clear_work_composers(self, work):
        if self.overwrite:
            work.composers.clear()
            work.lyricists.clear()
