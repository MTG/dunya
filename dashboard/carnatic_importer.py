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

import compmusic

import carnatic.models
from dashboard import release_importer
from dashboard.log import logger


class CarnaticReleaseImporter(release_importer.ReleaseImporter):
    _ArtistClass = carnatic.models.Artist
    _ArtistAliasClass = carnatic.models.ArtistAlias
    _ComposerClass = carnatic.models.Composer
    _ComposerAliasClass = carnatic.models.ComposerAlias
    _ReleaseClass = carnatic.models.Concert
    _RecordingClass = carnatic.models.Recording
    _InstrumentClass = carnatic.models.Instrument
    _WorkClass = carnatic.models.Work

    def remove_nonimported_items(self):
        # Artists as the performer of a concert
        concert_artists = self._ArtistClass.objects.filter(primary_concerts__mbid__in=self.imported_releases)
        concert_ids = [a.pk for a in concert_artists]

        # Artists who performed an instrument on a recording
        perf_artists = self._ArtistClass.objects.filter(instrumentperformance__recording__concertrecording__concert__mbid__in=self.imported_releases)
        perf_ids = [a.pk for a in perf_artists]

        artist_ids = list(set(concert_ids + perf_ids))

        # Releases that weren't in the imported list
        non_release = self._ReleaseClass.objects.exclude(mbid__in=self.imported_releases)
        non_release.delete()
        # Artists who aren't in the above two lists
        non_artist = self._ArtistClass.objects.exclude(pk__in=artist_ids).exclude(dummy=True)
        non_artist.delete()

        # Recordings not part of a concert that was just imported
        non_recording = self._RecordingClass.objects.exclude(concertrecording__concert__mbid__in=self.imported_releases)
        non_recording.delete()

        # Works not part of a recording part of a concert just imported
        non_work = self._WorkClass.objects.exclude(recordingwork__recording__concertrecording__concert__mbid__in=self.imported_releases)
        non_work.delete()

        # Composers not part of a work not part of a rec, part of concert
        non_composer = self._ComposerClass.objects.exclude(works__recordingwork__recording__concertrecording__concert__mbid__in=self.imported_releases).exclude(lyric_works__recordingwork__recording__concertrecording__concert__mbid__in=self.imported_releases)
        non_composer.delete()

    def _link_release_recording(self, concert, recording, trackorder, mnum, tnum):
        if not concert.recordings.filter(pk=recording.pk).exists():
            carnatic.models.ConcertRecording.objects.create(
                concert=concert, recording=recording, track=trackorder, disc=mnum, disctrack=tnum)

    def _add_work_attributes(self, work, mbwork, created):
        """ Read raaga and taala attributes from the webservice query
        and add them to the object """
        work.raaga = None
        work.taala = None
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
        carnatic.models.RecordingWork.objects.filter(recording=recording).delete()
        # A carnatic recording only has many works.
        for i, w in list(enumerate(works)):
            carnatic.models.RecordingWork.objects.create(work=w, recording=recording, sequence=i)

    def _apply_tags(self, recording, works, tags):
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

        # If we are missing a work, or if the work is missing raaga & taala, we should
        # add the information to the recording from the tag
        nowork = False
        if len(works) == 0:
            nowork = True
        for w in works:
            if not w.raaga or not w.taala:
                nowork = True
                break

        if noform or form.attrfromrecording or nowork:
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
            if a['attribute'] == u'Rāga (Carnatic)':
                return a['value']
        return None

    def _get_taala_mb(self, mb_work):
        for a in mb_work.get('attribute-list',[]):
            if a['attribute'] == u'Tāla (Carnatic)':
                return a['value']
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

    def _performance_type_to_instrument(self, perf_type, attrs):
        is_lead = False
        if perf_type == release_importer.RELATION_RECORDING_VOCAL:
            instr_name = "voice"
            if "lead vocals" in attrs:
                is_lead = True
        elif perf_type == release_importer.RELATION_RECORDING_INSTRUMENT:
            instr_name = attrs[-1]
            attrs = attrs[:-1]
            if "lead" in attrs:
                is_lead = True

        attributes = " ".join(attrs)
        instrument = self._get_instrument(instr_name)

        return instrument, attributes, is_lead

    def _add_recording_performance(self, recordingid, artistid, perf_type, attrs):
        logger.info("  Adding recording performance...")
        artist = self.add_and_get_artist(artistid)
        recording = carnatic.models.Recording.objects.get(mbid=recordingid)

        instrument, attributes, is_lead = self._performance_type_to_instrument(perf_type, attrs)

        if instrument:
            carnatic.models.InstrumentPerformance.objects.create(recording=recording, instrument=instrument, artist=artist, lead=is_lead, attributes=attributes)

    def _add_release_performance(self, releaseid, artistid, perf_type, attrs):
        logger.info("  Adding concert performance...")

        concert = carnatic.models.Concert.objects.get(mbid=releaseid)
        for rec in concert.recordings.all():
            self._add_recording_performance(rec.mbid, artistid, perf_type, attrs)

    def _add_release_artists_as_relationship(self, release, artist_credit):
        """ Convert release artists to lead performers on InstrumentPerformances """
        artists = release.artists.all()
        recordings = release.recordings.all()
        for r in recordings:
            for ip in r.instrumentperformance_set.all():
                if ip.artist in artists:
                    ip.lead = True
                    ip.save()

    def _clear_work_composers(self, work):
        work.composers.clear()
        work.lyricists.clear()
