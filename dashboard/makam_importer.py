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

import makam
import makam.models
import compmusic

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
        if self.overwrite:
            makam.models.RecordingWork.objects.filter(recording=recording).delete()
        sequence = 1
        for w in works:
            makam.models.RecordingWork.objects.create(work=w, recording=recording, sequence=sequence)
            sequence += 1

    def _get_makam(self, makamname):
        try:
            return makam.models.Makam.objects.unaccent_get(makamname)
        except makam.models.Makam.DoesNotExist:
            try:
                malias = makam.models.MakamAlias.objects.unaccent_get(makamname)
                return malias.makam
            except makam.models.MakamAlias.DoesNotExist:
                return None

    def _get_usul(self, usul):
        try:
            return makam.models.Usul.objects.unaccent_get(usul)
        except makam.models.Usul.DoesNotExist:
            try:
                ualias = makam.models.UsulAlias.objects.unaccent_get(usul)
                return ualias.usul
            except makam.models.UsulAlias.DoesNotExist:
                return None

    def _get_form(self, form):
        try:
            return makam.models.Form.objects.unaccent_get(form)
        except makam.models.Form.DoesNotExist:
            try:
                falias = makam.models.FormAlias.objects.unaccent_get(form)
                return falias.form
            except makam.models.FormAlias.DoesNotExist:
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

        # tags for no taksim
        notaksimt = [g for g in groups if g.get("form") != "taksim" and g.get("form") != "gazel"]

        # If a recording has two works, it will almost always have two of each
        # of the makam/form/usul tags. However, if one of the form tags is
        # Taksim it may only have one work (since the taksim is an improvisation)
        if len(works) == 1 and len(notaksimt) == 1:
            # If we have a work from two different recordings and the tags are
            # different, we'll add them anyway, but we need to check this because
            # it might be bad data.
            t = notaksimt[0]
            makam = self._get_makam(t.get("makam"))
            form = self._get_form(t.get("form"))
            usul = self._get_usul(t.get("usul"))
            w = works[0]
            if makam and w.makam.count() == 0:
                w.makam.add(makam)
            if usul and w.usul.count() == 0:
                w.usul.add(usul)
            if form and w.form.count() == 0:
                w.form.add(form)
        elif len(works) == len(notaksimt):
            pass
            # If a recording has two works and two sets of tags, we don't know which
            # tags go to which work, because works in musicbrainz are unordered.
            # In this case, flag them for manual interaction. TODO: How?
            # There are 2 possibilities:
            # If we have 2 works, a and b, and this recording x has both,
            # but y has only a and z has only b, then later in the import
            # this will be fixed
            # But, if work a only has this recording x, and z has b, we could
            # import z->b, and then other tags for x->a would work.

    def _get_instrument(self, instname):
        if not instname:
            return None
        try:
            return makam.models.Instrument.objects.alias_get(instname)
        except makam.models.Instrument.DoesNotExist:
            return None

    def _add_recording_performance(self, recordingid, artistid, instrument, is_lead):
        logger.info("  Adding recording performance...")
        artist = self.add_and_get_artist(artistid)
        instrument = self._get_instrument(instrument)
        if instrument:
            recording = makam.models.Recording.objects.get(mbid=recordingid)
            perf = makam.models.InstrumentPerformance(recording=recording, instrument=instrument, artist=artist, lead=is_lead)
            perf.save()

    def _add_release_performance(self, releaseid, artistid, instrument, is_lead):
        logger.info("  Adding release performance...")
        artist = self.add_and_get_artist(artistid)
        instrument = self._get_instrument(instrument)
        if instrument:
            release = makam.models.Release.objects.get(mbid=releaseid)
            # For each recording in the release, see if the relationship
            # already exists. If not, create it.
            for rec in release.recordings.all():
                if not makam.models.InstrumentPerformance.objects.filter(
                   recording=rec, instrument=instrument, artist=artist).exists():
                    perf = makam.models.InstrumentPerformance(recording=rec, instrument=instrument, artist=artist, lead=is_lead)
                    perf.save()

    def _clear_work_composers(self, work):
        if self.overwrite:
            work.composers.clear()
            work.lyricists.clear()

    def _add_work_attributes(self, work, mbwork, created):
        """ Read mb attributes from the webservice query
        and add them to the object """

        if created or self.overwrite:
            work.form.clear()
            work.usul.clear()
            work.makam.add(makam)

        if created or self.overwrite:
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
                    work.makam.clear()
                work.save()

    def _get_form_mb(self, mb_work):
        for a in mb_work.get('attribute-list',[]):
            if a['type'] == u'Form (Ottoman, Turkish)':
                return a['attribute']
        return None

    def _get_usul_mb(self, mb_work):
        for a in mb_work.get('attribute-list',[]):
            if a['type'] == u'Usul (Ottoman, Turkish)':
                return a['attribute']
        return None

    def _get_makam_mb(self, mb_work):
        for a in mb_work.get('attribute-list',[]):
            if a['type'] == u'Makam (Ottoman, Turkish)':
                return a['attribute']
        return None




