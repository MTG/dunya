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

import hindustani.models
from dashboard import release_importer
from dashboard.log import import_logger, logger


class HindustaniReleaseImporter(release_importer.ReleaseImporter):
    _ArtistClass = hindustani.models.Artist
    _ArtistAliasClass = hindustani.models.ArtistAlias
    _ComposerClass = hindustani.models.Composer
    _ComposerAliasClass = hindustani.models.ComposerAlias
    _ReleaseClass = hindustani.models.Release
    _RecordingClass = hindustani.models.Recording
    _InstrumentClass = hindustani.models.Instrument
    _WorkClass = hindustani.models.Work

    def _link_release_recording(self, release, recording, trackorder, mnum, tnum):
        if not release.recordings.filter(pk=recording.pk).exists():
            hindustani.models.ReleaseRecording.objects.create(
                release=release, recording=recording, track=trackorder, disc=mnum, disctrack=tnum
            )

    def _join_recording_and_works(self, recording, works):
        # A hindustani recording can have many works

        hindustani.models.WorkTime.objects.filter(recording=recording).delete()
        sequence = 1
        for w in works:
            hindustani.models.WorkTime.objects.create(work=w, recording=recording, sequence=sequence)
            sequence += 1

    def _apply_tags(self, recording, work, tags):
        raags = self._get_raag_tags(tags)
        taals = self._get_taal_tags(tags)
        layas = self._get_laya_tags(tags)
        forms = self._get_form_tags(tags)

        hindustani.models.RecordingTaal.objects.filter(recording=recording).delete()
        hindustani.models.RecordingLaya.objects.filter(recording=recording).delete()
        hindustani.models.RecordingRaag.objects.filter(recording=recording).delete()
        hindustani.models.RecordingForm.objects.filter(recording=recording).delete()

        if not layas:
            import_logger.warning("No laya tags found on recording")
        for l in layas:
            import_logger.info("Found laya tag %s", l)
            lpos = l[0]
            lob = self._get_laya(l[1])
            if lob:
                hindustani.models.RecordingLaya.objects.create(recording=recording, laya=lob, sequence=lpos)
            else:
                print("couldn't find a laya", l)

        if not taals:
            import_logger.warning("No taal tags found on recording")
        for t in taals:
            import_logger.info("Found taal tag %s", t)
            tpos = t[0]
            tob = self._get_taal(t[1])
            if tob:
                hindustani.models.RecordingTaal.objects.create(recording=recording, taal=tob, sequence=tpos)
            else:
                print("couldn't find a taal", t)

        if not raags:
            import_logger.warning("No raag tags found on recording")
        for r in raags:
            import_logger.info("Found raag tag %s", r)
            rpos = r[0]
            rob = self._get_raag(r[1])
            if rob:
                hindustani.models.RecordingRaag.objects.create(recording=recording, raag=rob, sequence=rpos)
            else:
                print("could't find a raag", r)

        if not forms:
            import_logger.warning("No form tags found on recording")
        for f in forms:
            import_logger.info("Found form tag %s", f)
            fpos = f[0]
            fob = self._get_form(f[1])
            if fob:
                hindustani.models.RecordingForm.objects.create(recording=recording, form=fob, sequence=fpos)
            else:
                print("couldn't find a form", f)

    def _get_raag_tags(self, taglist):
        ret = []
        for t in taglist:
            name = t["name"].lower()
            if compmusic.tags.has_raag(name):
                parsed = compmusic.tags.parse_raag(name)
                if parsed and parsed[0]:
                    ret.append(parsed)
        return ret

    def _get_taal_tags(self, taglist):
        ret = []
        for t in taglist:
            name = t["name"].lower()
            if compmusic.tags.has_taal(name):
                parsed = compmusic.tags.parse_taal(name)
                if parsed and parsed[0]:
                    ret.append(parsed)
        return ret

    def _get_laya_tags(self, taglist):
        ret = []
        for t in taglist:
            name = t["name"].lower()
            if compmusic.tags.has_laya(name):
                parsed = compmusic.tags.parse_laya(name)
                if parsed and parsed[0]:
                    ret.append(parsed)
        return ret

    def _get_form_tags(self, taglist):
        ret = []
        for t in taglist:
            name = t["name"].lower()
            if compmusic.tags.has_hindustani_form(name):
                parsed = compmusic.tags.parse_hindustani_form(name)
                if parsed and parsed[0]:
                    ret.append(parsed)
        return ret

    def _get_raag(self, rname):
        try:
            return hindustani.models.Raag.objects.fuzzy(rname)
        except hindustani.models.Raag.DoesNotExist:
            import_logger.warning("Cannot find raag '%s' in the database", rname)
            return None

    def _get_taal(self, tname):
        try:
            return hindustani.models.Taal.objects.fuzzy(tname)
        except hindustani.models.Taal.DoesNotExist:
            import_logger.warning("Cannot find taal '%s' in the database", tname)
            return None

    def _get_form(self, fname):
        try:
            return hindustani.models.Form.objects.fuzzy(fname)
        except hindustani.models.Form.DoesNotExist:
            import_logger.warning("Cannot find form '%s' in the database", fname)
            return None

    def _get_laya(self, lname):
        try:
            return hindustani.models.Laya.objects.fuzzy(lname)
        except hindustani.models.Laya.DoesNotExist:
            import_logger.warning("Cannot find laya '%s' in the database", lname)
            return None

    def _get_instrument(self, instname):
        try:
            return hindustani.models.Instrument.objects.get(name__iexact=instname)
        except hindustani.models.Instrument.DoesNotExist:
            import_logger.warning("Cannot find instrument '%s' in the database", instname)
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
        recording = hindustani.models.Recording.objects.get(mbid=recordingid)

        instrument, attributes, is_lead = self._performance_type_to_instrument(perf_type, attrs)

        if instrument:
            hindustani.models.InstrumentPerformance.objects.create(
                recording=recording, instrument=instrument, artist=artist, lead=is_lead, attributes=attributes
            )

    def _add_release_performance(self, releaseid, artistid, perf_type, attrs):
        logger.info("  Adding concert performance to all recordings...")
        release = hindustani.models.Release.objects.get(mbid=releaseid)
        for t in release.recordings.all():
            self._add_recording_performance(t.mbid, artistid, perf_type, attrs)
