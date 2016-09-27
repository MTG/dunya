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
from dashboard.log import import_logger
from dashboard import release_importer

import makam
import makam.models
import compmusic

DIALOGUE_ARTIST = "314e1c25-dde7-4e4d-b2f4-0a7b9f7c56dc"

class MakamReleaseImporter(release_importer.ReleaseImporter):
    _ArtistClass = makam.models.Artist
    _ArtistAliasClass = makam.models.ArtistAlias
    _ComposerClass = makam.models.Composer
    _ComposerAliasClass = makam.models.ComposerAlias
    _ReleaseClass = makam.models.Release
    _RecordingClass = makam.models.Recording
    _InstrumentClass = makam.models.Instrument
    _WorkClass = makam.models.Work

    def _link_release_recording(self, release, recording, trackorder, mnum, tnum):
        if not release.recordings.filter(pk=recording.pk).exists():
            makam.models.ReleaseRecording.objects.create(
                release=release, recording=recording, track=trackorder)

    def _join_recording_and_works(self, recording, works):
        # A makam recording can be of many works. Note that because works
        # in musicbrainz are unordered we don't know if this sequence is
        # correct. All of these recordings will need to be manually checked.
        makam.models.RecordingWork.objects.filter(recording=recording).delete()
        sequence = 1
        for w in works:
            makam.models.RecordingWork.objects.create(work=w, recording=recording, sequence=sequence)
            sequence += 1

    def _get_makam(self, makamname):
        try:
            return makam.models.Makam.objects.unaccent_get(makamname)
        except makam.models.Makam.DoesNotExist:
            malias = makam.models.MakamAlias.objects.unaccent_all(makamname)
            if malias.count():
                return malias[0].makam
            else:
                import_logger.warning("Cannot find makam '%s' in database", makamname)
                return None

    def _get_usul(self, usul):
        try:
            return makam.models.Usul.objects.unaccent_get(usul)
        except makam.models.Usul.DoesNotExist:
            try:
                ualias = makam.models.UsulAlias.objects.unaccent_get(usul)
                return ualias.usul
            except makam.models.UsulAlias.DoesNotExist:
                import_logger.warning("Cannot find usul '%s' in database", usul)
                return None

    def _get_form(self, form):
        try:
            return makam.models.Form.objects.unaccent_get(form)
        except makam.models.Form.DoesNotExist:
            try:
                falias = makam.models.FormAlias.objects.unaccent_get(form)
                return falias.form
            except makam.models.FormAlias.DoesNotExist:
                import_logger.warning("Cannot find form '%s' in database", form)
                return None

    def _get_makam_tags(self, taglist):
        ret = []
        for t in taglist:
            name = t["name"].lower()
            if compmusic.tags.has_makam(name):
                parsed = compmusic.tags.parse_makam(name)
                if parsed and parsed[1]:
                    ret.append(parsed)
        return ret

    def _get_usul_tags(self, taglist):
        ret = []
        for t in taglist:
            name = t["name"].lower()
            if compmusic.tags.has_usul(name):
                parsed = compmusic.tags.parse_usul(name)
                if parsed and parsed[1]:
                    ret.append(parsed)
        return ret

    def _get_form_tags(self, taglist):
        ret = []
        for t in taglist:
            name = t["name"].lower()
            if compmusic.tags.has_makam_form(name):
                parsed = compmusic.tags.parse_makam_form(name)
                if parsed and parsed[1]:
                    ret.append(parsed)
        return ret

    def _apply_tags(self, recording, works, tags):
        # If the form is Taksim and usul Serbest, this is an instrumental
        # improvisation. If form is Gazel, it is a vocal improvisation.
        # These don't have a work. Instead set recording.has_{taksim,gazel}
        # In this case, add the makam tag to the recording, because we
        # don't have a work for it.

        # TODO:
        # Double-check the works in musicbrainz to see if they have tags and
        # if so add their tags to the works.
        # We do have some taksims in musicbrainz as works. Eventually we should
        # remove them.

        makams = self._get_makam_tags(tags)
        forms = self._get_form_tags(tags)
        usuls = self._get_usul_tags(tags)

        groups = compmusic.tags.group_makam_tags(makams, forms, usuls)

        # Tags for taksim
        taksimt = [g for g in groups if g.get("form") == "taksim"]
        gazelt = [g for g in groups if g.get("form") == "gazel"]

        for t in taksimt:
            recording.has_taksim = True
            makam = self._get_makam(t.get("makam"))
            if makam:
                recording.makam.add(makam)
                recording.save()
        for t in gazelt:
            recording.has_gazel = True
            makam = self._get_makam(t.get("makam"))
            if makam:
                recording.makam.add(makam)
                recording.save()

    def _get_instrument(self, instname):
        if not instname:
            return None
        try:
            return makam.models.Instrument.objects.alias_get(instname)
        except makam.models.Instrument.DoesNotExist:
            import_logger.warning("Cannot find instrument '%s' in database", instname)
            return None

    def _performance_type_to_instrument(self, perf_type, attrs):
        if perf_type in [release_importer.RELATION_ORCHESTRA, release_importer.RELATION_PERFORMER, release_importer.RELATION_VOCAL]:
            try:
                instrument = makam.models.Instrument.objects.get(mbid=perf_type)
            except makam.models.Instrument.DoesNotExist:
                pass
            attributes = " ".join(attrs)
        elif perf_type == release_importer.RELATION_INSTRUMENT:
            if attrs:
                instr_name = attrs[-1]
                instrument = self._get_instrument(instr_name)
                attrs = attrs[:-1]
                attributes = " ".join(attrs)
            else:
                instrument = makam.models.Instrument.objects.get(mbid=release_importer.RELATION_INSTRUMENT)
                attributes = ""
        return instrument, attributes

    def _add_recording_performance(self, recordingid, artistid, perf_type, attrs):
        logger.info("  Adding recording performance...")
        artist = self.add_and_get_artist(artistid)

        instrument = None
        is_lead = False
        if "lead" in attrs:
            is_lead = True

        instrument, attributes = self._performance_type_to_instrument(perf_type, attrs)

        recording = makam.models.Recording.objects.get(mbid=recordingid)
        perf = makam.models.InstrumentPerformance.objects.create(recording=recording, instrument=instrument, artist=artist, attributes=attributes, lead=is_lead)

    def _add_release_performance(self, releaseid, artistid, perf_type, attrs):
        # We don't expect to see any release-level performance relationships, so we
        # raise an error to quit the whole import, so that we can fix it
        raise Exception("Performance relationship found on release %s" % releaseid)

    def _clear_work_composers(self, work):
        work.composers.clear()
        work.lyricists.clear()

    def _add_recording_artists(self, rec, artistids):
        rec.artists.clear()
        for a in artistids:
            # If the artist is [dialogue] the we don't show analysis.
            if a == DIALOGUE_ARTIST:
                rec.analyse = False
                rec.save()
            artist = self.add_and_get_artist(a)
            logger.info("  artist: %s" % artist)
            if not rec.artists.filter(pk=artist.pk).exists():
                logger.info("  - adding to artist list 2")
                rec.artists.add(artist)

    def _add_work_attributes(self, work, mbwork, created):
        """ Read mb attributes from the webservice query
        and add them to the object """

        work.form.clear()
        work.usul.clear()
        work.makam.clear()

        form_attr = self._get_form_mb(mbwork)
        usul_attr = self._get_usul_mb(mbwork)
        makam_attr = self._get_makam_mb(mbwork)
        if form_attr != "taksim" and form_attr != "gazel":
            form = self._get_form(form_attr)
            usul = self._get_usul(usul_attr)
            makam = self._get_makam(makam_attr)
            if form:
                work.form.add(form)
            if usul:
                work.usul.add(usul)
            if makam:
                work.makam.add(makam)
            work.save()

    def _get_form_mb(self, mb_work):
        for a in mb_work.get('attribute-list',[]):
            if a['attribute'] == u'Form (Ottoman, Turkish)':
                return a['value']
        return None

    def _get_usul_mb(self, mb_work):
        for a in mb_work.get('attribute-list',[]):
            if a['attribute'] == u'Usul (Ottoman, Turkish)':
                return a['value']
        return None

    def _get_makam_mb(self, mb_work):
        for a in mb_work.get('attribute-list',[]):
            if a['attribute'] == u'Makam (Ottoman, Turkish)':
                return a['value']
        return None

