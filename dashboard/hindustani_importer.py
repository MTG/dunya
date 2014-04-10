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

import hindustani
import data

class HindustaniReleaseImporter(release_importer.ReleaseImporter):
    _ArtistClass = hindustani.models.Artist
    _ArtistAliasClass = hindustani.models.ArtistAlias
    _ComposerClass = hindustani.models.Composer
    _ComposerAliasClass = hindustani.models.ComposerAlias
    _ReleaseClass = hindustani.models.Release
    _RecordingClass = hindustani.models.Recording
    _InstrumentClass = hindustani.models.Instrument
    _WorkClass = hindustani.models.Work


    def _link_release_recording(self, release, recording, trackorder):
        if not release.tracks.filter(pk=recording.pk).exists():
            hindustani.models.ReleaseRecording.objects.create(
                    release=release, recording=recording, track=trackorder)

    def join_recording_and_works(self, recording, works):
        # A hindustani recording can have many works
        sequence = 1
        for w in works:
            hindustani.models.WorkTime.objects.create(work=w, recording=recording, sequence=sequence)
            sequence += 1

    def _apply_tags(self, recording, work, tags):
        raags = self._get_raag_tags(tags)
        taals = self._get_taal_tags(tags)
        laays = self._get_laay_tags(tags)
        forms = self._get_form_tags(tags)

        if len(raags) != len(taals):
            print "Number of raagas and taalas doesn't match"
        if len(taals) != len(laays):
            print "number of taals and laays doesn't match"

        for t, l in zip(taals, laays):
            tpos = t[0]
            tob = _get_taal(t[1])
            lpos = l[0]
            lob = _get_laay(l[1])
            if tpos != lpos:
                print "positions differ"
            hindustani.models.RecordingTaal.objects.create(recording=recording, taal=tob, laay=lob, sequence=tpos)


        for r in raags:
            rpos = r[0]
            rob = _get_raag(r[1])
            hindustani.models.RecordingRaag.objects.create(recording=recording, raag=rob, sequence=rpos)

        for f in forms:
            fpos = f[0]
            fob = _get_form(f[1])
            hindustani.models.RecordingForm.objects.create(recording=recording, form=fob, sequence=fpos)
            pass

    def _get_raag_tags(self, taglist):
        ret = []
        for t in taglist:
            name = t["name"].lower()
            if compmusic.tags.has_raag(name):
                ret.append( compmusic.tags.parse_raag(name) )
        return ret

    def _get_taal_tags(self, taglist):
        ret = []
        for t in taglist:
            name = t["name"].lower()
            if compmusic.tags.has_taal(name):
                ret.append( compmusic.tags.parse_taal(name) )
        return ret

    def _get_laay_tags(self, taglist):
        ret = []
        for t in taglist:
            name = t["name"].lower()
            if compumusic.tags.has_laay(name):
                ret.append( compmusic.tags.parse_laay(name) )
        return ret

    def _get_form_tags(self, taglist):
        ret = []
        for t in taglist:
            name = t["name"].lower()
            if compumusic.tags.has_form(name):
                ret.append( compmusic.tags.parse_form(name) )
        return ret

    def _get_raag(self, rname):
        try:
            return hindustani.models.Taal.objects.get(transliteration=tname)
        except hindustani.models.Taal.DoesNotExist:
            return None

    def _get_taal(self, tname):
        try:
            return hindustani.models.Raag.objects.get(transliteration=tname)
        except hindustani.models.Raag.DoesNotExist:
            return None

    def _get_form(self, tname):
        try:
            return hindustani.models.Form.objects.get(transliteration=tname)
        except hindustani.models.Form.DoesNotExist:
            return None

    def _get_laay(self, tname):
        try:
            return hindustani.models.Laay.objects.get(transliteration=tname)
        except hindustani.models.Laay.DoesNotExist:
            return None

    def get_instrument(self, instname):
        try:
            return hindustani.models.Instrument.objects.get(name=instname)
        except hindustani.models.Instrument.DoesNotExist:
            try:
                alias = hindustani.models.InstrumentAlias.objects.get(name=instname)
                return alias.instrument
            except hindustani.models.InstrumentAlias.DoesNotExist:
                return None

    def _add_recording_performance(self, recordingid, artistid, instrument, is_lead):
        logger.info("  Adding recording performance...")
        artist = self.add_and_get_artist(artistid)
        instrument = self.get_instrument(instrument)
        if instrument:
            recording = hindustani.models.Recording.objects.get(mbid=recordingid)
            perf = hindustani.models.InstrumentPerformance(recording=recording, instrument=instrument, performer=artist, lead=is_lead)
            perf.save()

    def _add_release_performance(self, releaseid, artistid, instrument, is_lead):
        logger.info("  Adding concert performance to all tracks...")
        release = hindustani.models.Release.objects.get(mbid=releaseid)
        for t in release.tracks:
            self._add_recording_performance(t.mbid, artistid, instrument, is_lead)

