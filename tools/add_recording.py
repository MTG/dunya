#!/usr/bin/env python

import sys
import os
sys.path.insert(0, os.path.join(
        os.path.dirname(os.path.abspath(__file__)), ".."))

from dunya import settings
from django.core.management import setup_environ
setup_environ(settings)

from data.models import *

import musicbrainzngs as mb
mb.set_useragent("Dunya", "0.1")

import pprint

import logging
logging.basicConfig(level=logging.INFO)

def import_release(mbid):
    rel = mb.get_release_by_id(mbid, includes=["artists","recordings"])
    rel = rel["release"]

    mbid = rel["id"]
    logging.info("Adding release %s" % mbid)
    try:
        concert = Concert.objects.get(mbid=mbid)
    except Concert.DoesNotExist:
        concert = Concert(mbid=mbid)
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
        try:
            rec = Recording.objects.get(pk=recid)
        except Recording.DoesNotExist:
            rec = Recording(mbid=recid)
            mbrec = mb.get_recording_by_id(recid, includes=["tags", "work-rels"])

def add_and_get_artist(artistid):
    try:
        artist = Artist.objects.get(mbid=artistid)
    except Artist.DoesNotExist:
        logging.info("  creating artist")
        a = mb.get_artist_by_id(artistid)["artist"]
        artist = Artist(name=a["name"], mbid=artistid)
        if a.get("type") == "Person":
            artist.artist_type = "P"
        elif a.get("type") == "Group":
            artist.artist_type = "G"
        if a.get("gender") == "Male":
            artist.gender = "M"
        elif a.get("gender") == "Female":
            artist.gender = "F"
        artist.save()
    return artist

def add_and_get_recording(releaseid, recordingid):
    # Recording details
    pass

def add_work_for_recording(recordingid):
    # Add work
    # Composer
    # Raaga, Taala (from recording)

    # Performance information
    pass

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "usage: %s <release_mbid>" % (sys.argv[0], )
    else:
        import_release(sys.argv[1])

