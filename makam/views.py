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

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest
from django.conf import settings

import json
import data
from makam import models
import docserver

# Simple player for Georgi/Istanbul musicians
def makamplayer(request):
    return render(request, "makam/makamplayer.html")

def main(request):
    q = request.GET.get('q', None)
    recordings = None
    if q and q != '':
        recordings = models.Recording.objects.filter(title__contains=q).all()

    artist = request.GET.get('artist', None)
    form = request.GET.get('form', None)
    #makam = request.GET.get('makam', None)
    usul = request.GET.get('usul', None)


    artists = models.Composer.objects.order_by('name').all()
    forms = models.Form.objects.order_by('name').all()
    #makams = models.Makam.objects.order_by('name').all()
    usuls = models.Usul.objects.order_by('name').all()
    
    works = models.Work.objects
    if artist and artist != '':
        works = works.filter(composers=artist)
    if form and form != '':
        work = works.filter(form=form)
    if usul and usul != '':
        works = works.filter(usul=usul)
    
    ret = {
        "artists": artists, 
        #"makams": makams, 
        'usuls': usuls, 
        'forms': forms , 
        'artist': artist, 
        'form':form,
        #'makam':makam,
        'usul':usul,
        'works': works.all(),
        'recordings': recordings
        }
    return render(request, "makam/index.html", ret)

def composer(request, uuid, name=None):
    composer = get_object_or_404(models.Composer, mbid=uuid)

    ret = {"composer": composer
           }
    return render(request, "makam/composer.html", ret)

def artist(request, uuid, name=None):
    artist = get_object_or_404(models.Artist, mbid=uuid)

    instruments = artist.instruments()
    permission = data.utils.get_user_permissions(request.user)
    main_releases = artist.primary_concerts.with_permissions(False, permission).all()
    other_releases = artist.accompanying_releases()

    collaborating_artists = artist.collaborating_artists()

    main_release_d = {}
    for r in main_releases:
        instruments = r.instruments_for_artist(artist)
        main_release_d[r] = instruments

    other_release_d = {}
    for r in other_releases:
        instruments = r.instruments_for_artist(artist)
        other_release_d[r] = instruments

    ret = {"artist": artist,
           "instruments": instruments,
           "main_releases": main_release_d,
           "other_releases": other_release_d,
           "collaborating_artists": collaborating_artists
           }
    return render(request, "makam/artist.html", ret)

def release(request, uuid, title=None):
    release = get_object_or_404(models.Release, mbid=uuid)

    tracklist = release.tracklist()
    performers = release.performers()
    perfinst = []
    for p in performers:
        perfinst.append((p, release.instruments_for_artist(p)))

    ret = {"release": release,
           "tracklist": tracklist,
           "performers": perfinst
           }
    return render(request, "makam/release.html", ret)

def recording(request, uuid, title=None):
    recording = get_object_or_404(models.Recording, mbid=uuid)
   
    try:
        wave = docserver.util.docserver_get_url(recording.mbid, "makamaudioimages", "waveform32", 1, version=settings.FEAT_VERSION_IMAGE)
    except docserver.util.NoFileException:
        wave = None
    try:
        spec = docserver.util.docserver_get_url(recording.mbid, "makamaudioimages", "spectrum32", 1, version=settings.FEAT_VERSION_IMAGE)
    except docserver.util.NoFileException:
        spec = None
    try:
        small = docserver.util.docserver_get_url(recording.mbid, "makamaudioimages", "smallfull", version=settings.FEAT_VERSION_IMAGE)
    except docserver.util.NoFileException:
        small = None
    try:
        audio = docserver.util.docserver_get_mp3_url(recording.mbid)
    except docserver.util.NoFileException:
        audio = None
    try:
        tonic = docserver.util.docserver_get_contents(recording.mbid, "votedtonic", "tonic", version=settings.FEAT_VERSION_TONIC)
        notenames = ["A", "A♯", "B", "C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯"]
        tonic = round(float(tonic), 2)
        thebin = (12 * math.log(tonic / 440.0) / math.log(2)) % 12
        thebin = int(round(thebin))
        tonic = str(tonic)
        if thebin <= 11 and thebin >= 0:
            tonicname = notenames[thebin]
        else:
            print "bin is", thebin, "weird"
            print tonic
            tonicname = ""
    except docserver.util.NoFileException:
        tonic = None
        tonicname = None
    try:
        akshara = docserver.util.docserver_get_contents(recording.mbid, "rhythm", "aksharaPeriod", version=settings.FEAT_VERSION_RHYTHM)
        akshara = str(round(float(akshara), 3) * 1000)
    except docserver.util.NoFileException:
        akshara = None
    try:
        pitchtrackurl = docserver.util.docserver_get_url(recording.mbid, "makampitch", "pitch", version="0.4")
    except docserver.util.NoFileException:
        pitchtrackurl = "/document/by-id/%s/%s?subtype=%s&v=%s" % (recording.mbid, "makampitch", "pitch", "0.4")

    mbid = recording.mbid

    ret = {
           "recording": recording,
           "objecttype": "recording",
           "objectid": recording.id,
           "waveform": wave,
           "spectrogram": spec,
           "smallimage": small,
           "audio": audio,
           "tonic": tonic,
           "tonicname": tonicname,
           "akshara": akshara,
           "mbid": mbid,
           "pitchtrackurl": pitchtrackurl,
           "worklist": recording.worklist(),
    }
    return render(request, "makam/recording.html", ret)

def work(request, uuid, title=None):
    work = get_object_or_404(models.Work, mbid=uuid)

    ret = {"work": work
           }
    return render(request, "makam/work.html", ret)

def makambyid(request, makamid, name=None):
    makam = get_object_or_404(models.Makam, pk=makamid)
    return redirect(makam.get_absolute_url(), permanent=True)

def makam(request, uuid, name=None):
    makam = get_object_or_404(models.Makam, uuid=uuid)

    ret = {"makam": makam
           }
    return render(request, "makam/makam.html", ret)

def usulbyid(request, usulid, name=None):
    usul = get_object_or_404(models.Usul, pk=usulid)
    return redirect(usul.get_absolute_url(), permanent=True)

def usul(request, uuid, name=None):
    usul = get_object_or_404(models.Usul, uuid=uuid)

    ret = {"usul": usul
           }
    return render(request, "makam/usul.html", ret)

def formbyid(request, formid, name=None):
    form = get_object_or_404(models.Form, pk=formid)
    return redirect(form.get_absolute_url(), permanent=True)

def form(request, uuid, name=None):
    form = get_object_or_404(models.Form, uuid=uuid)

    ret = {"form": form
           }
    return render(request, "makam/form.html", ret)

def instrumentbyid(request, instrumentid, name=None):
    instrument = get_object_or_404(models.Instrument, pk=instrumentid)
    return redirect(instrument.get_absolute_url(), permanent=True)

def instrument(request, uuid, name=None):
    instrument = get_object_or_404(models.Instrument, mbid=uuid, hidden=False)

    ret = {"instrument": instrument
           }
    return render(request, "makam/instrument.html", ret)

def symbtr(request, uuid):
    """ The symbtr view returns the data of this item from
    the docserver, except sets a download hint for the browser
    and sets the filename to be the symbtr name """

    sym = get_object_or_404(models.SymbTr, uuid=uuid)
    types = ("txt", "midi", "pdf", "xml", "mu2")
    fmt = request.GET.get("format", "txt")
    if fmt not in types:
        return HttpResponseBadRequest("Unknown format parameter")

    slug = "symbtr%s" % fmt
    filetype = get_object_or_404(docserver.models.SourceFileType, slug=slug)
    filename = "%s.%s" % (sym.name, filetype.extension)
    response = docserver.views.download_external(request, uuid, slug)
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename

    return response
