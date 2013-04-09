#!/usr/bin/env python

import sys
import os
sys.path.insert(0, os.path.join(
        os.path.dirname(os.path.abspath(__file__)), ".."))

from dunya import settings
from django.core.management import setup_environ
setup_environ(settings)

from carnatic.models import *
import data.models
import parse_tags

import musicbrainzngs as mb
mb.set_useragent("Dunya", "0.1")
mb.set_rate_limit(False)
mb.set_hostname("sitar.s.upf.edu:8090")

import pprint

import logging
logging.basicConfig(level=logging.INFO)

def make_mb_source(url):
    sn = data.models.SourceName.objects.get(name="MusicBrainz")
    source = data.models.Source.objects.create(source_name=sn, uri=url)
    return source

def import_release(mbid):
    rel = mb.get_release_by_id(mbid, includes=["artists","recordings"])
    rel = rel["release"]

    mbid = rel["id"]
    logging.info("Adding release %s" % mbid)
    try:
        concert = Concert.objects.get(mbid=mbid)
    except Concert.DoesNotExist:
        concert = Concert(mbid=mbid, title=rel["title"])
        source = make_mb_source("http://musicbrainz.org/release/%s" % mbid)
        concert.source = source
        concert.save()
        for a in rel["artist-credit"]:
            artistid = a["artist"]["id"]
            artist = add_and_get_artist(artistid)
            logging.info("  artist: %s" % artist)
            concert.artists.add(artist)
    recordings = []
    for medium in rel["medium-list"]:
        for track in medium["track-list"]:
            recordings.append(track["recording"]["id"])
    for recid in recordings:
        recording = add_and_get_recording(recid)
        concert.tracks.add(recording)


def add_and_get_artist(artistid):
    try:
        artist = Artist.objects.get(mbid=artistid)
    except Artist.DoesNotExist:
        logging.info("  adding artist %s" % (artistid, ))
        a = mb.get_artist_by_id(artistid)["artist"]
        artist = Artist(name=a["name"], mbid=artistid)
        source = make_mb_source("http://musicbrainz.org/artist/%s" % artistid)
        artist.source = source
        if a.get("type") == "Person":
            artist.artist_type = "P"
        elif a.get("type") == "Group":
            artist.artist_type = "G"
        if a.get("gender") == "Male":
            artist.gender = "M"
        elif a.get("gender") == "Female":
            artist.gender = "F"
        dates = a.get("life-span")
        if dates:
            artist.begin = dates.get("begin")
            artist.end = dates.get("end")
        artist.save()
    return artist

def _get_raaga(taglist):
    ret = []
    for t in taglist:
        name = t["name"].lower()
        if parse_tags.has_raaga(name):
            ret.append(parse_tags.parse_raaga(name))
    return ret

def _get_taala(taglist):
    ret = []
    for t in taglist:
        name = t["name"].lower()
        if parse_tags.has_taala(name):
            ret.append(parse_tags.parse_taala(name))
    return ret

def add_and_get_recording(recordingid):
    try:
        rec = Recording.objects.get(mbid=recordingid)
    except Recording.DoesNotExist:
        logging.info("  adding recording %s" % (recordingid,))
        mbrec = mb.get_recording_by_id(recordingid, includes=["tags", "work-rels", "artist-rels"])
        mbrec = mbrec["recording"]
        raagas = _get_raaga(mbrec.get("tag-list", []))
        taalas = _get_taala(mbrec.get("tag-list", []))
        mbwork = None
        for work in mbrec.get("work-relation-list", []):
            if work["type"] == "performance":
                mbwork = add_and_get_work(work["target"], raagas, taalas)
        rec = Recording(mbid=recordingid, work=mbwork)
        source = make_mb_source("http://musicbrainz.org/recording/%s" % recordingid)
        rec.source = source
        rec.length = mbrec.get("length")
        rec.title = mbrec["title"]
        rec.save()
        for perf in mbrec.get("artist-relation-list", []):
            if perf["type"] == "vocal":
                artistid = perf["target"]
                is_lead = "lead" in perf["attribute-list"]
                add_performance(recordingid, artistid, "vocal", is_lead)
            elif perf["type"] == "instrument":
                artistid = perf["target"]
                attrs = perf.get("atrribute-list", [])
                is_lead = False
                if "lead" in attrs:
                    is_lead = "True"
                    attrs.remove("lead")
                inst = perf["attribute-list"][0]
                add_performance(recordingid, artistid, inst, is_lead)
    return rec

def add_and_get_work(workid, raagas, taalas):
    try:
        w = Work.objects.get(mbid=workid)
    except Work.DoesNotExist:
        mbwork = mb.get_work_by_id(workid, includes=["artist-rels"])["work"]
        w = Work(title=mbwork["title"], mbid=workid)
        source = make_mb_source("http://musicbrainz.org/work/%s" % workid)
        w.source = source
        w.save()
        for seq, rname in raagas:
            r = add_and_get_raaga(rname)
            if r:
                WorkRaaga.objects.create(work=w, raaga=r, sequence=seq)
            else:
                logging.warn("Cannot find raaga: %s" % rname)
        for seq, tname in taalas:
            t = add_and_get_taala(tname)
            if t:
                WorkTaala.objects.create(work=w, taala=t, sequence=seq)
            else:
                logging.warn("Cannot find taala: %s" % tname)
        for artist in mbwork.get("artist-relation-list", []):
            if artist["type"] == "composer":
                composer = add_and_get_composer(artist["target"])
                w.composer = composer
                w.save()
            elif artist["type"] == "lyricist":
                pass
    return w

def add_and_get_composer(artistid):
    try:
        composer = Composer.objects.get(mbid=artistid)
    except Composer.DoesNotExist:
        logging.info("  adding composer %s" % (artistid, ))
        a = mb.get_artist_by_id(artistid)["artist"]
        composer = Composer(name=a["name"], mbid=artistid)
        source = make_mb_source("http://musicbrainz.org/artist/%s" % artistid)
        composer.source = source
        if a.get("gender") == "Male":
            composer.gender = "M"
        elif a.get("gender") == "Female":
            composer.gender = "F"
        dates = a.get("life-span")
        if dates:
            composer.begin = dates.get("begin")
            composer.end = dates.get("end")
        composer.save()

    return composer

def add_and_get_raaga(raaganame):
    try:
        return Raaga.objects.fuzzy(name=raaganame)
    except Raaga.DoesNotExist, e:
        try:
            alias = RaagaAlias.objects.fuzzy(name=raaganame)
            return alias.raaga
        except RaagaAlias.DoesNotExist, e:
            return None

def add_and_get_taala(taalaname):
    try:
        return Taala.objects.fuzzy(name=taalaname)
    except Taala.DoesNotExist, e:
        try:
            alias = TaalaAlias.objects.fuzzy(name=taalaname)
            return alias.taala
        except TaalaAlias.DoesNotExist, e:
            return None

def add_performance(recordingid, artistid, instrument, is_lead):
    logging.info("  Adding performance...")
    artist = add_and_get_artist(artistid)
    instrument = add_and_get_instrument(instrument)
    recording = Recording.objects.get(mbid=recordingid)
    perf = InstrumentPerformance(recording=recording, instrument=instrument, performer=artist, lead=is_lead)
    perf.save()

def add_and_get_instrument(instname):
    return Instrument.objects.fuzzy(name=instname)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "usage: %s <release_mbid>" % (sys.argv[0], )
    else:
        import_release(sys.argv[1])

