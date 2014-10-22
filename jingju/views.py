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
from django.conf import settings
import math

import docserver.util

def main(request):
    return render(request, "jingju/index.html")


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

def recording(request, mbid, length):
    try:
        wave = docserver.util.docserver_get_url(mbid, "audioimages", "waveform32", 1, version=settings.FEAT_VERSION_IMAGE)
    except docserver.util.NoFileException:
        wave = None
    try:
        spec = docserver.util.docserver_get_url(mbid, "audioimages", "spectrum32", 1, version=settings.FEAT_VERSION_IMAGE)
    except docserver.util.NoFileException:
        spec = None
    try:
        small = docserver.util.docserver_get_url(mbid, "audioimages", "smallfull", version=settings.FEAT_VERSION_IMAGE)
    except docserver.util.NoFileException:
        small = None
    try:
        audio = docserver.util.docserver_get_mp3_url(mbid)
    except docserver.util.NoFileException:
        audio = None

    try:
        pitchtrackurl = docserver.util.docserver_get_url(mbid, "normalisedpitch", "packedpitch", version=settings.FEAT_VERSION_NORMALISED_PITCH)
        histogramurl = docserver.util.docserver_get_url(mbid, "normalisedpitch", "drawhistogram", version=settings.FEAT_VERSION_NORMALISED_PITCH)
    except docserver.util.NoFileException:
        pitchtrackurl = "/document/by-id/%s/%s?subtype=%s&v=%s" % (mbid, "normalisedpitch", "packedpitch", settings.FEAT_VERSION_NORMALISED_PITCH)
        histogramurl = "/document/by-id/%s/%s?subtype=%s&v=%s" % (mbid, "normalisedpitch", "drawhistogram", settings.FEAT_VERSION_NORMALISED_PITCH)

    ret = {
           "recording": recording,
           "waveform": wave,
           "spectrogram": spec,
           "smallimage": small,
           "audio": audio,
           "mbid": mbid,
           "pitchtrackurl": pitchtrackurl,
           "histogramurl": histogramurl,
           "length": length,
           "length_format": length_format(length),
           }

    return render(request, "jingju/%s.html" % mbid, ret)

def rec_0b5dd02b(request):
    length = 602
    return recording(request, "0b5dd02b-d93e-4b44-81a3-d789f29ddb7d", length)

def rec_3dcae41a(request):
    return recording(request, "0b5dd02b-d93e-4b44-81a3-d789f29ddb7d")

def rec_415d9fcc(request):
    return recording(request, "0b5dd02b-d93e-4b44-81a3-d789f29ddb7d")

def rec_87b5c1b2(request):
    return recording(request, "0b5dd02b-d93e-4b44-81a3-d789f29ddb7d")
