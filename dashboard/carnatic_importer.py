# -*- coding: utf-8 -*-
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
import json
import musicbrainzngs

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

    def _link_release_recording(self, concert, recording, trackorder, mnum, tnum):
        if not concert.recordings.filter(pk=recording.pk).exists():
            carnatic.models.ConcertRecording.objects.create(
                concert=concert, recording=recording, track=trackorder, disc=mnum, disctrack=tnum)

    def _join_recording_and_works(self, recording, works):
        # A carnatic recording only has many works.
        for i, w in list(enumerate(works)):
            carnatic.models.RecordingWork.objects.create(work=w, recording=recording, sequence=i)

    def _apply_tags(self, recording, works, tags):
        for w in works:
            if self.overwrite:
                w.raaga.clear()
                w.taala.clear()
            
            # Check that there is not more than one form
            forms = recording.forms.all()
            if len(forms) > 1:
                raise release_importer.ImportFailedException('More than form for a recording')
            elif len(forms) < 1:
                form = self._get_form_tag(tags)
                if form:
                    recording.forms.append(form)
                    recording.save()
                else:
                    raise release_importer.ImportFailedException("The recording doesn't have form")
            else:
                form = forms[0]

            # Check release and work has the same raaga and taala
            raaga_tag = self._get_raaga_tags(tags)
            taala_tag = self._get_taala_tags(tags)
            mb_work = musicbrainzngs.get_work_by_id(w.mbid)
            raaga_work = self._get_raaga_mb(mb_work)
            taala_work = self._get_taala_mb(mb_work)

            if raaga_tag:
                raaga_tag = self._get_raaga(raaga_tag)
            if raaga_work:
                raaga_work = self._get_raaga(raaga_work)

            if taala_tag:
                taala_tag = self._get_taala(taala_tag)
            if taala_work:
                taala_work = self._get_taala(taala_work)
            
            if (raaga_tag and raaga_work and raaga_tag != raaga_work) or (taala_tag and taala_work and taala_tag != taala_work):
                raise release_importer.ImportFailedException('Inconsistency found at Musicbrainz between recording tag and work raaga or taala')
            if form.attrfromrecording:
               r = raaga_tag
               t = taala_tag
            else:
               r = raaga_work
               t = taala_work

            # Create the relation with Raaga and Taala
            if r:
                carnatic.models.RecordingRaaga.objects.create(recording=recording, raaga=r, sequence=1)
            if t:
                carnatic.models.WorkTaala.objects.create(recording=recording, taala=t, sequence=1)
        else:
            # If we have no works, we don't need to do this
            return
    
    def _get_form_tag(self, tags):
        for t in tags:
            name = t["name"].lower()
            if compmusic.tags.has_carnatic_form(name):
                return compmusic.tags.parse_carnatic_form(name)
        return None


    def _get_raaga_mb(self, mb_work):
        for a in mb_work['work'].get('attribute-list',[]):
            if a['type'] == u'Rāga (Carnatic)':
                return compmusic.tags.parse_raaga(a['attribute'])
        return None

    def _get_taala_mb(self, mb_work):
        for a in mb_work['work'].get('attribute-list',[]):
            if a['type'] == u'Tāla (Carnatic)':
                return compmusic.tags.parse_taala(a['attribute'])
        return None

    def _get_raaga_tags(self, taglist):
        for t in taglist:
            name = t["name"].lower()
            if compmusic.tags.has_raaga(name):
                return compmusic.tags.parse_raaga(name)
        return None

    def _get_taala_tags(self, taglist):
        for t in taglist:
            name = t["name"].lower()
            if compmusic.tags.has_taala(name):
                return compmusic.tags.parse_taala(name)
        return None

    def _get_raaga(self, raaganame):
        try:
            return carnatic.models.Raaga.objects.fuzzy(raaganame)
        except carnatic.models.Raaga.DoesNotExist:
            logger.warn("Cannot find raaga: %s" % raaganame)
            return None

    def _get_taala(self, taalaname):
        try:
            return carnatic.models.Taala.objects.fuzzy(taalaname)
        except carnatic.models.Taala.DoesNotExist:
            logger.warn("Cannot find taala: %s" % taalaname)
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
