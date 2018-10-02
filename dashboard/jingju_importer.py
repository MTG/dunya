# -*- coding: utf-8 -*-
from __future__ import print_function
import compmusic

import jingju.models
from dashboard import release_importer
from dashboard.log import logger


ROLE_TYPE_DIC= {u'旦': 'dan',
                u'老旦': 'laodan',
                u'老生': 'laosheng',
                u'小生': 'xiaosheng',
                u'净': 'jing',
                u'丑': 'chou'}

class JingjuReleaseImporter(release_importer.ReleaseImporter):
    _ArtistClass = jingju.models.Artist
    _ArtistAliasClass = jingju.models.ArtistAlias
    # _ComposerClass = carnatic.models.Composer
    # _ComposerAliasClass = carnatic.models.ComposerAlias
    _ReleaseClass = jingju.models.Release
    _RecordingClass = jingju.models.Recording
    _InstrumentClass = jingju.models.Instrument
    _WorkClass = jingju.models.Work

    def _join_recording_and_works(self, recording, works):
        if works:
            work = works[0]
            mbwork = compmusic.mb.get_work_by_id(work.mbid, includes=["artist-rels", "work-rels", "series-rels"])["work"]
            if mbwork.has_key('series-relation-list'):
                mbscore = mbwork['series-relation-list'][0]['series']
                score = jingju.models.Score.objects.create(name=mbscore['name'], uuid=mbscore['id'])
                work.score = score
            if mbwork.has_key('work-relation-list'):
                mbplay = mbwork['work-relation-list'][0]['work']
                play = jingju.models.Play.objects.create(title=mbplay['title'], uuid=mbplay['id'])
                work.play = play
            work.save()
            recording.work = work
            recording.save()

    def _apply_tags(self, recording, works, tags):
        for tag in tags:
            shengqiangbanshi = jingju.models.ShengqiangBanshi.objects.create(name=tag['name'])
            recording.shengqiangbanshi.add(shengqiangbanshi)
            recording.save()

    def _link_release_recording(self, release, recording, trackorder, mnum, tnum):
        if not release.recordings.filter(pk=recording.pk).exists():
            jingju.models.RecordingRelease.objects.create(
                release=release, recording=recording, track=trackorder, disc=mnum, disctrack=tnum)

    def _add_release_performance(self, releaseid, artistid, perf_type, attrs):
        # logger.info("  Adding concert performance...")

        release = jingju.models.Release.objects.get(mbid=releaseid)
        for rec in release.recordings.all():
            self._add_recording_performance(rec.mbid, artistid, perf_type, attrs)

    def _add_recording_performance(self, recordingid, artistid, perf_type, attrs):
        # logger.info("  Adding recording performance...")
        artist = self.add_and_get_artist(artistid)
        recording = jingju.models.Recording.objects.get(mbid=recordingid)

        instrument = self._performance_type_to_instrument(perf_type, attrs)

        if instrument:
            jingju.models.RecordingInstrumentalist.objects.create(recording=recording, instrument=instrument, artist=artist)
            artist.instrument = instrument
            artist.recording_set.add(recording)
            artist.save()

    def _performance_type_to_instrument(self, perf_type, attrs):
        instrument = None
        if perf_type == release_importer.RELATION_RELEASE_INSTRUMENT:
            instr_name = attrs[-1]
            instrument = self._get_instrument(instr_name)

        return instrument

    def _get_instrument(self, instname):
        try:
            return jingju.models.Instrument.objects.get(name__iexact=instname)
        except jingju.models.Instrument.DoesNotExist:
            return None

    def _add_recording_artists(self, rec, artistids):
        rec.performers .clear()
        for a in artistids:
            # If the artist is [dialogue] the we don't show analysis.
            artist = self.add_and_get_artist(a)
            logger.info("  artist: %s" % artist)
            if not rec.performers.filter(pk=artist.pk).exists():
                logger.info("  - adding to artist list 2")
                rec.performers.add(artist)

    def add_and_get_artist(self, artistid):
        if artistid in self.imported_artists:
            print("Artist already updated in this import. Not doing it again")
            return self._ArtistClass.objects.get(mbid=artistid)

        mbartist = compmusic.mb.get_artist_by_id(artistid, includes=["url-rels", "artist-rels", "aliases", "tags"])["artist"]
        artist = self._create_artist_object(mbartist)
        # print mbartist['id']
        if mbartist.has_key('tag-list'):
            for tag in mbartist['tag-list']:
                tagname = tag['name']
                if tagname in ROLE_TYPE_DIC:
                    role_type = jingju.models.RoleType.objects.get(name__iexact=tagname)
                    artist.role_type = role_type
                    artist.save()

        self.imported_artists.append(artistid)
        return artist

    def _create_artist_object(self, mbartist):
        artist = super(JingjuReleaseImporter, self)._create_artist_object(self._ArtistClass, self._ArtistAliasClass, mbartist)
        alias = mbartist['sort-name'].replace(", ", " ")
        artist.alias = alias
        return artist
