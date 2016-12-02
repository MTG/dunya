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

import os
import json
import data
import docserver
import search
import pysolr
import zipfile
import StringIO

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.utils.safestring import SafeString
from makam import models

# Simple player for Georgi/Istanbul musicians
def makamplayer(request):
    return render(request, "makam/makamplayer.html")

def guest_login(request):
    if not request.user.is_authenticated():
        user = User.objects.get(username='guest')
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

def guest_logout(request):
    if request.user.is_authenticated() and request.user.username == 'guest':
        logout(request)


def searchcomplete(request):
    term = request.GET.get("term")
    ret = []
    error = False
    if term:
        try:
            suggestions = search.autocomplete(term)
            ret = []
            for l in suggestions:
                label = l['title_t']
                if 'composer_s' in l:
                    label += ' - ' +l['composer_s']
                if 'artists_s' in l:
                    artists = l['artists_s']
                    if len(artists) > 40:
                        artists = artists[:40] + "..."
                    label += ' - ' + artists
                if 'mbid_s' not in l:
                    l['mbid_s'] = ''

                ret.append({"id": l['object_id_i'], "label": label, "category": l['type_s'], "mbid": l['mbid_s']})
        except pysolr.SolrError:
            error = True
    return HttpResponse(json.dumps(ret), content_type="application/json")

def results(request):
    term = request.GET.get("q")
    ret = {}
    error = False
    if term:
        try:
            suggestions = search.autocomplete(term)
            for l in suggestions:
                doc = {'label': l['title_t'], 'id': l['object_id_i'],}
                if l['type_s'] not in ret:
                    ret[l['type_s']] = []

                if 'mbid_s' not in l:
                    l['mbid_s'] = ''
                if 'composer_s' in l:
                    doc['composer'] = l['composer_s']
                if 'artists_s' in l:
                    doc['artists'] = l['artists_s']

                doc['mbid'] = l['mbid_s']
                ret[l['type_s']].append(doc)
        except pysolr.SolrError:
            error = True
    return render(request, "makam/results.html", {'results': ret, 'error': error})


def main(request):
    q = request.GET.get('q', '')

    s_artist = request.GET.get('artist', '')
    s_perf = request.GET.get('performer', '')
    s_form = request.GET.get('form', '')
    s_makam = request.GET.get('makam', '')
    s_usul = request.GET.get('usul', '')
    s_work= request.GET.get('work', '')

    artist = ""
    if s_artist and s_artist != '':
        artist = models.Composer.objects.get(id=s_artist)
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
    work = ""
    if s_work and s_work != '':
        work = models.Work.objects.get(id=s_work)


    url = None
    recordings = None
    results = None
    if s_work != '' or s_artist != '' or s_perf != '' or s_form != '' or s_usul != '' or s_makam != '' or q:
        recordings, url = get_works_and_url(s_work, s_artist, s_form, s_usul, s_makam, s_perf, q)
        if q and q!='':
            url["q"] = "q=" + SafeString(q.encode('utf8'))

        results = len(recordings) != 0

        paginator = Paginator(recordings, 25)
        page = request.GET.get('page')
        try:
            recordings = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            recordings = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            recordings = paginator.page(paginator.num_pages)
    if not url:
        url = {
                "q": "q=%s" % SafeString(q.encode('utf8')),
                "usul": "usul=%s" % s_usul,
                "work": "work=%s" % s_work,
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
        'work': work,
        'recordings': recordings,
        'results': results,
        'q': q,
        'params': url,
    }
    return render(request, "makam/work_list.html", ret)

def filter_directory(request):
    elem = request.GET.get('elem', None)

    q = request.GET.get('q', None)

    artist = request.GET.get('artist', '')
    perf = request.GET.get('performer', '')
    form = request.GET.get('form', '')
    makam = request.GET.get('makam', '')
    usul = request.GET.get('usul', '')
    work= request.GET.get('work', '')

    recordings, url = get_works_and_url(work, artist, form, usul, makam, perf, q, elem)
    if q and q!='':
        url["q"] = "q=" + SafeString(q.encode('utf8'))

    recording_ids = recordings.values_list('id', flat=True).all()
    if elem == "makam":
        elems = models.Makam.objects.filter(work__recording__id__in=recording_ids).order_by('name').distinct()
    elif elem == "form":
        elems = models.Form.objects.filter(work__recording__id__in=recording_ids).order_by('name').distinct()
    elif elem == "usul":
        elems = models.Usul.objects.filter(work__recording__id__in=recording_ids).order_by('name').distinct()
    elif elem == "artist":
        elems = models.Composer.objects.filter(works__recording__id__in=recording_ids).order_by('name').distinct() | \
            models.Composer.objects.filter(lyric_works__recording__id__in=recording_ids).order_by('name').distinct()
    elif elem == "performer":
        e_perf = models.Artist.objects.filter(instrumentperformance__recording__id__in=recording_ids).distinct() | \
                 models.Artist.objects.filter(recording__id__in=recording_ids).distinct()
        elems = e_perf.order_by('name').distinct()

    return  render(request, "makam/display_directory.html", {"elem": elem, "elems": elems, "params": url})

def get_works_and_url(work, artist, form, usul, makam, perf, q, elem=None):
    recordings = models.Recording.objects
    url = {}
    if q and q!='':
        ids = list(models.Work.objects.unaccent_get(q).values_list('pk', flat=True))
        recordings = recordings.filter(works__id__in=ids) | recordings.filter(title__contains=q)

    if elem != "artist":
        if artist and artist != '':
            recordings = recordings.filter(works__composers=artist) | recordings.filter(works__lyricists=artist)
        url["artist"] = "artist=" + artist
    if elem != "form":
        if form and form != '':
            if form == '17':
                recordings = recordings.filter(has_gazel=True)
            if form == '67':
                recordings = recordings.filter(has_taksim=True)
            else:
                recordings= recordings.filter(works__form=form)
        url["form"] = "form=" + form
    if elem != "work":
        if work and work != '':
            recordings = recordings.filter(works=work)
        url["work"] = "work=" + work
    if elem != "usul":
        if usul and usul != '':
            recordings = recordings.filter(works__usul=usul)
        url["usul"] = "usul=" + usul
    if elem != "makam":
        if makam and makam != '':
            recordings = recordings.filter(works__makam=makam)
        url["makam"] = "makam=" + makam
    if elem != "performer":
        if perf and perf != '':
            recordings = recordings.filter(instrumentperformance__artist=perf) | \
                    recordings.filter(release__artists=perf)
        url["perf"] = "performer=" + perf

    recordings = recordings.distinct().order_by('title')
    return recordings, url


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
            "indexmapurl": indexmapurl,
        })

def basic_lyric_alignment(request, uuid, title=None):
    recording = models.Recording()
    recording.title = "碧云天黄花地西风紧” 《西厢记》（崔莺莺）"
    recordingmbid = uuid
    mbid = uuid
    try:
        lyricsalignurl = docserver.util.docserver_get_url(mbid, "lyrics-align", "alignedLyricsSyllables", 1, version="0.1")
    except docserver.exceptions.NoFileException:
        lyricsalignurl = None
    try:
        audio = docserver.util.docserver_get_mp3_url(mbid)
    except docserver.exceptions.NoFileException:
        audio = None
    ret = {
           "recording": recording,
           "objecttype": "recording",
           "audio": audio,
           "mbid": mbid,
           "lyricsalignurl": lyricsalignurl,
           "recordinglengthfmt": "5:29",
           "recordinglengthseconds": "329",
    }
    return render(request, "makam/basic_lyric_alignment.html", ret)




def lyric_alignment(request, uuid, title=None):
    recording = get_object_or_404(models.Recording, mbid=uuid)
    mbid = recording.mbid

    intervalsurl = "/score?v=0.2&subtype=intervals"
    scoreurl = "/score?v=0.2&subtype=score&part=1"
    documentsurl = "/document/by-id/"
    phraseurl = "/segmentphraseseg?v=0.1&subtype=segments"

    try:
        audio = docserver.util.docserver_get_mp3_url(mbid)
    except docserver.exceptions.NoFileException:
        audio = None

    try:
        max_pitch = docserver.util.docserver_get_json(mbid, "tomatodunya", "pitchmax", 1, version="0.1")
        min_pitch = max_pitch['min']
        max_pitch = max_pitch['max']
    except docserver.exceptions.NoFileException:
        max_pitch = None
        min_pitch = None

    ret = {
           "recording": recording,
           "objecttype": "recording",
           "objectid": recording.id,
           "audio": audio,
           "mbid": mbid,
           "worklist": recording.worklist(),
           "scoreurl": scoreurl,
           "intervalsurl": intervalsurl,
           "documentsurl": documentsurl,
           "max_pitch": max_pitch,
           "min_pitch": min_pitch,
           "phraseurl": phraseurl,
    }

    urls = recordings_urls()
    urls["notesalignurl"] = [("lyrics-align", "alignedLyricsSyllables", 1, "0.1")]
    urls["alignsectionsurl"] = [("lyrics-align", "sectionlinks", 1, "0.1")]
    for u in urls.keys():
        for option in urls[u]:
            try:
                success_content = docserver.util.docserver_get_url(mbid, option[0], option[1],
                        option[2], version=option[3])
                ret[u] = success_content
                break
            except docserver.exceptions.NoFileException:
                ret[u] = None

    return render(request, "makam/lyric_alignment.html", ret)

def recordings_urls(include_img_and_bin=True):
    ret = {
            "notesalignurl": [("jointanalysis", "notes", 1, "0.1")],
            "pitchtrack": [("jointanalysis", "pitch", 1, "0.1"),
                ('audioanalysis', 'pitch', 1, '0.1')],
            "pitchclass": [('jointanalysis', 'pitch_class_distribution', 1, '0.1'),
                ('audioanalysis', 'pitch_class_distribution', 1, '0.1')],
            "tempourl": [("jointanalysis", "tempo", 1, "0.1")],
            "histogramurl": [("jointanalysis", "pitch_distribution", 1, "0.1"),
                ("audioanalysis", "pitch_distribution", 1, "0.1")],
            "notemodelsurl": [("jointanalysis", "note_models", 1, "0.1"),
                ("audioanalysis", "note_models", 1, "0.1")],
            "sectionsurl": [("jointanalysis", "sections", 1, "0.1")],
            "tonicurl": [( "jointanalysis", "tonic", 1, "0.1"),
                ("audioanalysis", "tonic", 1, "0.1")],
            "ahenkurl": [("jointanalysis", "transposition", 1, "0.1")],
            "worksurl": [("jointanalysis", "works_intervals", 1, "0.1")],
            "melodic_progression": [("jointanalysis", "melodic_progression", 1,
                "0.1")],
            "waveform": [("makamaudioimages", "waveform8", 1, 0.3)],
            "smallimage": [("makamaudioimages", "smallfull", 1, 0.3)],
            "audiometadata": [("audioanalysis", "metadata", 1, "0.1")]
    }
    if include_img_and_bin:
        ret["spectrogram"] = [("makamaudioimages", "spectrum8", 1, 0.3)]
        ret["pitchtrackurl"] = [("tomatodunya", "pitch", 1, "0.1")]

    return ret

def recording(request, uuid, title=None):
    recording = get_object_or_404(models.Recording, mbid=uuid)
    recording_doc = docserver.models.Document.objects.filter(
            external_identifier=recording.mbid, collections__slug='makam-open')
    if recording_doc.count():
        guest_login(request)
    else:
        guest_logout(request)
    start_time = request.GET.get("start", 0)
    mbid = recording.mbid

    intervalsurl = "/score?v=0.2&subtype=intervals"
    scoreurl = "/score?v=0.2&subtype=score&part=1"
    documentsurl = "/document/by-id/"
    phraseurl = "/segmentphraseseg?v=0.1&subtype=segments"

    try:
        audio = docserver.util.docserver_get_mp3_url(mbid)
    except docserver.exceptions.NoFileException:
        audio = None

    try:
        max_pitch = docserver.util.docserver_get_json(mbid, "tomatodunya", "pitchmax", 1, version="0.1")
        min_pitch = max_pitch['min']
        max_pitch = max_pitch['max']
    except docserver.exceptions.NoFileException:
        max_pitch = None
        min_pitch = None

    has_score = docserver.models.Document.objects.filter(
            external_identifier__in=list(recording.works.values_list('mbid', flat=True).all()),
            sourcefiles__file_type__extension='xml').count()

    ret = {
           "recording": recording,
           "objecttype": "recording",
           "objectid": recording.id,
           "audio": audio,
           "mbid": mbid,
           "worklist": recording.worklist(),
           "scoreurl": scoreurl,
           "intervalsurl": intervalsurl,
           "documentsurl": documentsurl,
           "max_pitch": max_pitch,
           "min_pitch": min_pitch,
           "phraseurl": phraseurl,
           "start_time": start_time,
           "has_score": has_score
    }

    urls = recordings_urls()
    for u in urls.keys():
        curr_option = 0
        for option in urls[u]:
            try:
                curr_option += 1
                if option[0] not in ('tomatodunya', 'makamaudioimages'):
                    content = docserver.util.docserver_get_json(mbid, option[0],
                        option[1], option[2], version=option[3])
                    if content != None and (len(urls[u]) == curr_option or len(content.keys())):
                        success_content = docserver.util.docserver_get_url(mbid,
                            option[0], option[1], option[2], version=option[3])
                        ret[u] = success_content
                        break
                else:
                    success_content = docserver.util.docserver_get_url(mbid,
                            option[0], option[1], option[2], version=option[3])
                    ret[u] = success_content

            except docserver.exceptions.NoFileException:
                ret[u] = None

    return render(request, "makam/recording.html", ret)

def download_derived_files(request, uuid, title=None):
    recording = get_object_or_404(models.Recording, mbid=uuid)
    mbid = recording.mbid

    filenames = []

    urls = recordings_urls(False)

    for w in recording.works.all():
        document = docserver.models.Document.objects.filter(external_identifier=w.mbid)
        if len(document) == 1:
            files = document[0].derivedfiles.filter(outputname='score',
                    module_version__version="0.2")

            if len(files) == 1:
                for n in range(files[0].num_parts):
                    filenames.append((docserver.util.docserver_get_filename(w.mbid,
                        'score', 'score', n+1, '0.2'), '%s-%s-%d-%d' %
                        ('score', 'score', n+1, 2)))
            score = document[0].sourcefiles.filter(file_type__extension='xml')
            if len(score) == 1:
                filenames.append((score[0].fullpath, '%s-%s-%d-%d' %
                        ('score', 'score', 1, 2)))
        try:
            filenames.append((docserver.util.docserver_get_filename(w.mbid,
                'scoreanalysis', 'metadata', 1, '0.1'), '%s-%s-%d-%d' %
                ('scoreanalysis', 'metadata', 1, 1)))
        except docserver.exceptions.NoFileException:
            pass

    keys = sorted(urls.keys(), reverse=True)
    for u in keys:
        for option in urls[u]:
            try:
                if option[0] in ('tomatodunya', 'makamaudioimages'):
                    filenames.append((docserver.util.docserver_get_filename(mbid, option[0],
                        option[1], option[2], version=option[3]), '%s-%s-%d-%d' %
                        (option[0], option[1], 1, int(float(option[3])*10))))
                    break
                content = docserver.util.docserver_get_json(mbid, option[0], option[1],
                        option[2], version=option[3])
                if content and (type(content) is list or
                        (len(content.keys()) and
                            ('pitch' in content or content[content.keys()[0]]))):
                    filenames.append((docserver.util.docserver_get_filename(mbid, option[0],
                        option[1], option[2], version=option[3]), '%s-%s-%d-%d' %
                        (option[0], option[1], 1, int(float(option[3])*10))))
                    break
            except docserver.exceptions.NoFileException:
                pass

    zip_subdir = "derivedfiles_%s" % mbid
    zip_filename = "%s.zip" % zip_subdir

    s = StringIO.StringIO()
    zf = zipfile.ZipFile(s, "w")
    for f in filenames:
        fpath = f[0]
        filename, file_extension = os.path.splitext(f[0])
        fname = f[1]
        # Replace name fonly for smallfull case
        zip_path = os.path.join(zip_subdir, fname.replace('smallfull',
            'melodic_progression') + file_extension)

        # Add file, at correct path
        zf.write(fpath, zip_path)
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

    return resp


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
