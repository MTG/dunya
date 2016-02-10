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

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.utils.safestring import SafeString

import json
import data
from makam import models
import docserver

# Simple player for Georgi/Istanbul musicians
def makamplayer(request):
    return render(request, "makam/makamplayer.html")

def main(request):
    q = request.GET.get('q', '')
    
    s_artist = request.GET.get('artist', '')
    s_perf = request.GET.get('performer', '')
    s_form = request.GET.get('form', '')
    s_makam = request.GET.get('makam', '')
    s_usul = request.GET.get('usul', '')

    artist = ""
    if s_artist and s_artist != '': 
        artist = models.Artist.objects.get(id=s_artist)
    perf = ""
    if s_perf and s_perf != '': 
        perf = models.Artist.objects.get(id=s_perf)
    form = ""
    if s_form and s_form != '':
        form = models.Form.objects.get(id=s_form)
    usul = ""
    if s_usul and s_usul != '': 
        usul = models.Usul.objects.get(id=s_usul)
    makam = ""
    if s_makam and s_makam != '': 
        makam = models.Makam.objects.get(id=s_makam)
    
    url = None
    works = None
    results = None
    if s_artist != '' or s_perf != '' or s_form != '' or s_usul != '' or s_makam != '' or q:
        works, url = get_works_and_url(s_artist, s_form, s_usul, s_makam, s_perf, q)
        results = len(works) != 0
   
        paginator = Paginator(works, 25)
        page = request.GET.get('page')
        try:
            works = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            works = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            works = paginator.page(paginator.num_pages)
    if not url:
        url = {
                "q": "q=%s" % SafeString(q),
                "usul": "usul=%s" % s_usul, 
                "form": "form=%s" % s_form, 
                "artist": "artist=%s" % s_artist, 
                "makam": "makam=%s" % s_makam, 
                "perf": "performer=%s" % s_perf 
                }
     
    ret = {
        'artist': artist, 
        'perf': perf, 
        'makam': makam, 
        'usul': usul, 
        'form': form,
        'works': works,
        'results': results,
        'q': q,
        'params': url,
    }
    return render(request, "makam/index.html", ret)

def filter_directory(request):
    elem = request.GET.get('elem', None)
    
    q = request.GET.get('q', None)
    
    artist = request.GET.get('artist', '')
    perf = request.GET.get('performer', '')
    form = request.GET.get('form', '')
    makam = request.GET.get('makam', '')
    usul = request.GET.get('usul', '')
   
    works, url = get_works_and_url(artist, form, usul, makam, perf, None, elem)
    
    if q and q!='':
        url["q"] = "q=" + q

    if elem == "makam":
        elems = models.Makam.objects.filter(work__in=works.all()).order_by('name').distinct()
    elif elem == "form": 
        elems = models.Form.objects.filter(work__in=works.all()).order_by('name').distinct()
    elif elem == "usul":
        elems = models.Usul.objects.filter(work__in=works.all()).order_by('name').distinct()
    elif elem == "artist":
        elems = models.Artist.objects.filter(recording__works__in=works.all()).order_by('name').distinct()
    elif elem == "performer":
        e_perf = models.Artist.objects.all()
        elems = e_perf.order_by('name').distinct()
    return  render(request, "makam/display_directory.html", {"elem": elem, "elems": elems, "params": url})

def get_works_and_url(artist, form, usul, makam, perf, q, elem=None):
    works = models.Work.objects
    if q and q!='':
        works = works.unaccent_get(q) | works.filter(recording__title__contains=q)
    
    url = {}
    if elem != "artist": 
        if artist and artist != '': 
            works = works.filter(composers=artist)
        url["artist"] = "artist=" + artist 
    if elem != "form": 
        if form and form != '': 
            works = works.filter(form=form) 
        url["form"] = "form=" + form 
    if elem != "usul": 
        if usul and usul != '': 
            works = works.filter(usul=usul) 
        url["usul"] = "usul=" + usul 
    if elem != "makam": 
        if makam and makam != '': 
            works = works.filter(makam=makam) 
        url["makam"] = "makam=" + makam 
    if elem != "performer": 
        if perf and perf != '':
            works = works.filter(recordingwork__recording__instrumentperformance__artist=perf) | \
                    works.filter(recordingwork__recording__release__artists=perf)
        url["perf"] = "performer=" + perf 

    works = works.distinct().order_by('title')
    return works, url

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

def work_score(request, uuid, title=None):
    work = None
    works = models.Work.objects.filter(mbid=uuid)
    if len(works):
        work = works[0]
    
    scoreurl = "/document/by-id/%s/score?v=0.1&subtype=score&part=1" % uuid
    phraseurl = "/document/by-id/%s/segmentphraseseg?v=0.1&subtype=segments" % uuid
    indexmapurl = "/document/by-id/%s/score?v=0.1&subtype=indexmap" % uuid

    return render(request, "makam/work_score.html", {
            "work": work,
            "phraseurl": phraseurl, 
            "scoreurl": scoreurl,
            "indexmapurl": indexmapurl
        })


def recording(request, uuid, title=None):
    recording = get_object_or_404(models.Recording, mbid=uuid)
    mbid = recording.mbid
    
    intervalsurl = "/score?v=0.1&subtype=intervals" 
    scoreurl = "/score?v=0.1&subtype=score&part=1"
    indexmapurl = "/score?v=0.1&subtype=indexmap"
    documentsurl = "/document/by-id/"
    phraseurl = "/segmentphraseseg?v=0.1&subtype=segments"

    try:
        wave = docserver.util.docserver_get_url(mbid, "makamaudioimages", "waveform8", 1, version=0.2)
    except docserver.util.NoFileException:
        wave = None
    try:
        spec = docserver.util.docserver_get_url(mbid, "makamaudioimages", "spectrum8", 1, version=0.2)
    except docserver.util.NoFileException:
        spec = None
    try:
        small = docserver.util.docserver_get_url(mbid, "makamaudioimages", "smallfull", version=0.2)
    except docserver.util.NoFileException:
        small = None
    try:
        audio = docserver.util.docserver_get_mp3_url(mbid)
    except docserver.util.NoFileException:
        audio = None
    
    try:
        akshara = docserver.util.docserver_get_contents(mbid, "rhythm", "aksharaPeriod", version=settings.FEAT_VERSION_RHYTHM)
        akshara = str(round(float(akshara), 3) * 1000)
    except docserver.util.NoFileException:
        akshara = None
    try:
        pitchtrackurl = docserver.util.docserver_get_url(mbid, "dunyapitchmakam", "pitch", version="0.2")
    except docserver.util.NoFileException:
        pitchtrackurl = "/document/by-id/%s/%s?subtype=%s&v=%s" % (mbid, "dunyapitchmakam", "pitch", "0.2")
     
    try:
        notesalignurl = docserver.util.docserver_get_url(mbid, "scorealign", "notesalign", 1, version="0.2")
    except docserver.util.NoFileException:
        notesalignurl = None 
   
    try:
        histogramurl = docserver.util.docserver_get_url(mbid, "correctedpitchmakam", "histogram", 1, version="0.2")
    except docserver.util.NoFileException:
        histogramurl = None 

    try:
        notemodelsurl = docserver.util.docserver_get_url(mbid, "correctedpitchmakam", "notemodels", 1, version="0.2")
    except docserver.util.NoFileException:
        notemodelsurl = None 

    try:
        sectionsurl = docserver.util.docserver_get_url(mbid, "scorealign", "sectionlinks", 1, version="0.2")
    except docserver.util.NoFileException:
        sectionsurl = None 
     
    try:
        max_pitch = docserver.util.docserver_get_json(mbid, "dunyapitchmakam", "pitchmax", 1, version="0.2")
        min_pitch = max_pitch['min']
        max_pitch = max_pitch['max']
    except docserver.util.NoFileException:
        max_pitch = None
        min_pitch = None
    try:
        tonicurl = docserver.util.docserver_get_url(mbid, "tonictempotuning", "tonic", 1, version="0.1")
    except docserver.util.NoFileException:
        tonicurl = None
    try:
        ahenkurl = docserver.util.docserver_get_url(mbid, "correctedpitchmakam", "ahenk", 1, version="0.2")
    except docserver.util.NoFileException:
        ahenkurl = None

    try:
        worksurl = docserver.util.docserver_get_url(mbid, "correctedpitchmakam", "works_intervals", 1, version="0.2")
    except docserver.util.NoFileException:
        worksurl = None

    try:
        lyricsalignurl = docserver.util.docserver_get_url(mbid, "lyrics-align", "alignedLyricsSyllables", 1, version="0.1")
    except docserver.util.NoFileException:
        lyricsalignurl = None

    ret = {
           "recording": recording,
           "objecttype": "recording",
           "objectid": recording.id,
           "waveform": wave,
           "spectrogram": spec,
           "smallimage": small,
           "audio": audio,
           "tonicurl": tonicurl,
           "akshara": akshara,
           "mbid": mbid,
           "pitchtrackurl": pitchtrackurl,
           "worklist": recording.worklist(),
           "scoreurl": scoreurl,
           "indexmapurl": indexmapurl,
           "sectionsurl": sectionsurl, 
           "notesalignurl": notesalignurl,
           "intervalsurl": intervalsurl,
           "documentsurl": documentsurl,
           "histogramurl": histogramurl,
           "notemodelsurl": notemodelsurl,
           "lyricsalignurl": lyricsalignurl,
           "max_pitch": max_pitch,
           "min_pitch": min_pitch,
           "worksurl": worksurl,
           "phraseurl": phraseurl,
           "ahenkurl": ahenkurl
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
