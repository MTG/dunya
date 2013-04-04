#!/usr/bin/env python

import sys
import os
sys.path.insert(0, os.path.join(
        os.path.dirname(os.path.abspath(__file__)), ".."))

import musicbrainzngs as mb
mb.set_useragent("Dunya", "0.1")
mb.set_rate_limit(False)
mb.set_hostname("sitar.s.upf.edu:8090")

def get_tags_for_recording(recordingid):
    mbrec = mb.get_recording_by_id(recordingid, includes=["tags", "work-rels", "artist-rels"])
    mbrec = mbrec["recording"]
    return [t['name'] for t in mbrec.get("tag-list", [])]

def get_release(release):
    print >>sys.stderr, "release", release
    rel = mb.get_release_by_id(release, includes=["artists","recordings"])
    rel = rel["release"]
    recordings = []
    for medium in rel["medium-list"]:
        for track in medium["track-list"]:
            recordings.append(track["recording"]["id"])
    tags = []
    for recid in recordings:
        tags.extend(get_tags_for_recording(recid))
    return list(set(tags))

def main():
    tags = []
    for line in open(sys.argv[1]):
        try:
            tags.extend(get_release(line.strip()))
        except mb.musicbrainz.ResponseError:
            pass
    for i in list(set(tags)):
        print i

if __name__ == "__main__":
    main()
