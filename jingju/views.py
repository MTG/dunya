# -*- coding: UTF-8 -*-

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

from django.shortcuts import render
from django.http import Http404
import math
import json

import docserver.util

recordings = None

def main(request):
    global recordings
    if not recordings:
        recordings = json.load(open("jingju/trackdata.json"))
    data = []
    for k, d in recordings.items():
        print d
        data.append({"title": d["title"]["val"], "recording": k, "release": d["release"]["val"]})
    ret = {"recordings": data}

    return render(request, "jingju/index.html", ret)


def length_format(length):
    numsecs = length
    minutes = math.floor(numsecs / 60.0)
    hours = math.floor(minutes / 60.0)
    minutes = math.floor(minutes - hours * 60)
    seconds = math.floor(numsecs - hours * 3600 - minutes * 60)
    if hours:
        val = "%02d:%02d:%02d" % (hours, minutes, seconds)
    else:
        val = "%02d:%02d" % (minutes, seconds)

    return val

def recording(request, uuid):
    global recordings
    if not recordings:
        recordings = json.load(open("jingju/trackdata.json"))
    if uuid not in recordings:
        raise Http404()

    mbid = uuid
    drawoctave = 1 if recordings[uuid]["octave"]["val"] == "yes" else 0
    length = int(recordings[uuid]["duration"]["val"])

    try:
        spec = docserver.util.docserver_get_url(mbid, "audioimages", "spectrum32", 1)
    except docserver.util.NoFileException:
        spec = None
    try:
        small = docserver.util.docserver_get_url(mbid, "audioimages", "smallfull")
    except docserver.util.NoFileException:
        small = None
    try:
        audio = docserver.util.docserver_get_mp3_url(mbid)
    except docserver.util.NoFileException:
        audio = None

    try:
        pitchtrackurl = docserver.util.docserver_get_url(mbid, "normalisedpitch", "packedpitch")
        histogramurl = docserver.util.docserver_get_url(mbid, "normalisedpitch", "drawhistogram")
    except docserver.util.NoFileException:
        pitchtrackurl = "/document/by-id/%s/%s?subtype=%s&v=%s" % (mbid, "normalisedpitch", "packedpitch")
        histogramurl = "/document/by-id/%s/%s?subtype=%s&v=%s" % (mbid, "normalisedpitch", "drawhistogram")

    ret = {
           "recording": recording,
           "spectrogram": spec,
           "smallimage": small,
           "audio": audio,
           "mbid": mbid,
           "pitchtrackurl": pitchtrackurl,
           "histogramurl": histogramurl,
           "length": length,
           "length_format": length_format(length),
           "meta": recordings[uuid],
           "drawoctave": drawoctave
           }

    return render(request, "jingju/recording.html", ret)

