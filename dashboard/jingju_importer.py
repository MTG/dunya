import compmusic
import re

import jingju.models
from dashboard import release_importer
from dashboard.log import logger


class JingjuReleaseImporter(release_importer.ReleaseImporter):
    _ArtistClass = jingju.models.Artist
    _ArtistAliasClass = None
    _ComposerClass = jingju.models.Composer
    _ComposerAliasClass = None
    _ReleaseClass = jingju.models.Release
    _RecordingClass = jingju.models.Recording
    _InstrumentClass = jingju.models.Instrument
    _WorkClass = jingju.models.Work

    def _join_recording_and_works(self, recording, works):
        if works:
            work = works[0]
            mbwork = compmusic.mb.get_work_by_id(work.mbid, includes=["artist-rels", "work-rels", "series-rels"])[
                "work"
            ]
            if "series-relation-list" in mbwork:
                mbscore = mbwork["series-relation-list"][0]["series"]
                score = jingju.models.Score.objects.create(name=mbscore["name"], uuid=mbscore["id"])
                work.score = score
            if "work-relation-list" in mbwork:
                mbplay = mbwork["work-relation-list"][0]["work"]
                play = jingju.models.Play.objects.create(title=mbplay["title"], uuid=mbplay["id"])
                work.play = play
            work.save()
            recording.work = work
            recording.save()

    def _get_sqbs_codes_from_tags(self, tags):
        sqbs_re = r"(sqbs[0-9]{3}): ?(.+)"
        codes = set()
        for tag in tags:
            name = tag["name"]
            match = re.match(sqbs_re, name)
            if match:
                codes.add(match.group(1))
        return list(codes)

    def _apply_tags(self, recording, works, tags):
        sqbs_codes = self._get_sqbs_codes_from_tags(tags)
        for code in sqbs_codes:
            try:
                shengqiangbanshi = jingju.models.ShengqiangBanshi.objects.get(code=code)
                recording.shengqiangbanshi.add(shengqiangbanshi)
                recording.save()
            except jingju.models.ShengqiangBanshi.DoesNotExist:
                logger.error(f"Cannot find sqbs with code {code}")
                raise

    def _link_release_recording(self, release, recording, trackorder, mnum, tnum):
        if not release.recordings.filter(pk=recording.pk).exists():
            jingju.models.RecordingRelease.objects.create(
                release=release, recording=recording, track=trackorder, disc=mnum, disctrack=tnum
            )

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
            jingju.models.RecordingInstrumentalist.objects.create(
                recording=recording, instrument=instrument, artist=artist
            )
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
        rec.performers.clear()
        for a in artistids:
            # If the artist is [dialogue] the we don't show analysis.
            artist = self.add_and_get_artist(a)
            logger.info(f"  artist: {artist}")
            if not rec.performers.filter(pk=artist.pk).exists():
                rec.performers.add(artist)

    def add_and_get_artist(self, artistid):
        if artistid in self.imported_artists:
            print("Artist already updated in this import. Not doing it again")
            return self._ArtistClass.objects.get(mbid=artistid)

        mbartist = compmusic.mb.get_artist_by_id(artistid, includes=["url-rels", "artist-rels", "aliases", "tags"])[
            "artist"
        ]
        artist = self._create_artist_object(self._ArtistClass, self._ArtistAliasClass, mbartist)

        sortname = mbartist["sort-name"].replace(", ", " ")
        artist.romanisation = sortname

        role_type = self._get_roletype_from_tags(mbartist.get("tag-list", []))
        if role_type:
            artist.role_type = role_type
        artist.save()

        self.imported_artists.append(artistid)
        return artist

    def _get_roletype_from_tags(self, tags):
        rt_re = r"(hd[0-9]{2}): ?(.+)"
        roletypes = set()
        for tag in tags:
            tagname = tag["name"]
            match = re.match(rt_re, tagname)
            if match:
                roletypes.add(match.group(1))
        roletypes = sorted(list(roletypes), reverse=True)
        # We may get multiple roletypes, but they're ordered in lexical order due to the code,
        # so we can get the most specific one by sorting them in reverse and taking the first one
        if roletypes:
            try:
                role_type = jingju.models.RoleType.objects.get(code=roletypes[0])
                return role_type
            except jingju.models.RoleType.DoesNotExist:
                logger.error(f"cannot find roletype with code {roletypes[0]}")
        return None
