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

    def _add_work_attributes(self, work, mbwork, created):
        """ Read raaga and taala attributes from the webservice query
        and add them to the object """
        if created or self.overwrite:
            raaga_attr = self._get_raaga_mb(mbwork)
            taala_attr = self._get_taala_mb(mbwork)
            if raaga_attr:
                raaga = self._get_raaga(raaga_attr)
                if raaga:
                    work.raaga = raaga
            if taala_attr:
                taala = self._get_taala(taala_attr)
                if taala:
                    work.taala = taala
            work.save()

    def _join_recording_and_works(self, recording, works):
        if self.overwrite:
            carnatic.models.RecordingWork.objects.filter(recording=recording).delete()
        # A carnatic recording only has many works.
        for i, w in list(enumerate(works)):
            carnatic.models.RecordingWork.objects.create(work=w, recording=recording, sequence=i)

    def _apply_tags(self, recording, works, tags):
        if self.overwrite:
            recording.forms.clear()
            recording.raagas.clear()
            recording.taalas.clear()

        # Check that there is not more than one form
        noform = False
        forms = recording.forms.all()
        if len(forms) > 1:
            raise release_importer.ImportFailedException('TODO: Support more than one form per recording')
        elif len(forms) < 1:
            form = self._get_form_tag(tags)
            if form:
                # TODO: If there is more than one form, set sequence properly
                carnatic.models.RecordingForm.objects.create(recording=recording, form=form, sequence=1)
            else:
                # If we have no form, we import anyway and put the tags on the recording
                noform = True
        else:
            form = forms[0]

        if noform or form.attrfromrecording:
            # Create the relation with Raaga and Taala

            raaga_tag = self._get_raaga_tags(tags)
            taala_tag = self._get_taala_tags(tags)

            if raaga_tag:
                r = self._get_raaga(raaga_tag)
                if r:
                    carnatic.models.RecordingRaaga.objects.create(recording=recording, raaga=r, sequence=1)

            if taala_tag:
                t = self._get_taala(taala_tag)
                if t:
                    carnatic.models.RecordingTaala.objects.create(recording=recording, taala=t, sequence=1)
        elif not form.attrfromrecording:
            # In this case, we read attributes from the work. If the work has no attributes
            # we should add these tags to the recording anyway.
            pass


    def _get_form_tag(self, tags):
        for t in tags:
            name = t["name"].lower()
            if compmusic.tags.has_carnatic_form(name):
                form_tag = compmusic.tags.parse_carnatic_form(name)
                # forms are returned in (num, tag) - for now we just
                # assume there is one
                form = self._get_form(form_tag[1])
                return form
        return None


    def _get_raaga_mb(self, mb_work):
        for a in mb_work.get('attribute-list',[]):
            if a['type'] == u'Rāga (Carnatic)':
                return a['attribute']
        return None

    def _get_taala_mb(self, mb_work):
        for a in mb_work.get('attribute-list',[]):
            if a['type'] == u'Tāla (Carnatic)':
                return a['attribute']
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

    def _get_form(self, form):
        try:
            return carnatic.models.Form.objects.fuzzy(form)
        except carnatic.models.Form.DoesNotExist:
            logger.warn("Cannot find form: %s" % form)
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
