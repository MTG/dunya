#!/usr/bin/env python

import sys
import os
sys.path.insert(0, os.path.join(
        os.path.dirname(os.path.abspath(__file__)), ".."))

import musicbrainzngs as mb
mb.set_useragent("Dunya", "0.1")
mb.set_rate_limit(False)
mb.set_hostname("sitar.s.upf.edu:8090")

def get_inst_for_recording(recordingid):
    mbrec = mb.get_recording_by_id(recordingid, includes=["tags", "work-rels", "artist-rels"])
    mbrec = mbrec["recording"]
    insts = []
    for perf in mbrec.get("artist-relation-list", []):
        if perf["type"] == "vocal":
            insts.append("vocal")
        elif perf["type"] == "instrument":
            i = perf["attribute-list"][0]
            insts.append(i)
    return list(set(insts))

def get_release(release):
    print >>sys.stderr, "release", release
    rel = mb.get_release_by_id(release, includes=["artists","recordings"])
    rel = rel["release"]
    recordings = []
    for medium in rel["medium-list"]:
        for track in medium["track-list"]:
            recordings.append(track["recording"]["id"])
    insts = []
    for recid in recordings:
        insts.extend(get_inst_for_recording(recid))
    print list(set(insts))
    return list(set(insts))

def main():
    insts = []
    for line in open(sys.argv[1]):
        try:
            insts.extend(get_release(line.strip()))
        except mb.musicbrainz.ResponseError:
            pass
    for i in list(set(insts)):
        print i

if __name__=="__main__":
    main()
