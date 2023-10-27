#!/usr/bin/env python

from __future__ import print_function

import os
import uuid

import eyed3
import musicbrainzngs as mb

from dashboard import makam_importer
from data.models import Collection

mb.set_useragent("Dunya", "0.1")
mb.set_rate_limit(False)
mb.set_hostname("musicbrainz.org")

'''Script for uploading audio files on Makam collection and creating Recordings:
   take turkish-makam collection
   add new release, use this release when there is no release for the recording
   for each recording create an Recording and then call add_and_get_recording in
   release_importer.'''


def main(path, fake_release_mbid):
    releases = {}
    # Get all the mbid of the recordings
    onlyfiles = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    for i in onlyfiles:
        head, tail = os.path.split(i)
        filename, file_extension = os.path.splitext(i)
        if file_extension == '.mp3':
            c = eyed3.load(os.path.join(path, i))
            mbid = c.tag.unique_file_ids.get("http://musicbrainz.org").render()[33:]
            try:
                rel = mb.get_recording_by_id(mbid, includes=["releases"])
                release = None
                if len(rel['recording']['release-list']):
                    # create release
                    release = rel['recording']['release-list'][0]['id']
                else:
                    release = fake_release_mbid
                    # use *fake* release
                if release not in releases:
                    releases[release] = []
                releases[release].append(mbid)
            except:
                print(f"couldn't find a release for the recording {mbid}")
                continue
    coll = Collection.objects.get(mbid="544f7aec-dba6-440c-943f-103cf344efbb")
    r = makam_importer.MakamReleaseImporter(coll)
    for i in releases.keys():
        r.import_release(i, "")
        for j in releases[i]:
            r.add_and_get_recording(j)


if __name__ == "__main__":
    uuid = uuid.uuid4()
    main('/home/andres/Downloads/makam-stream/audio', uuid)
