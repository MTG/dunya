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

import StringIO
import json
import os
import zipfile

from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

import docserver.exceptions
import docserver.models
import docserver.util
import docserver.views
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
    term = request.GET.get("input")
    ret = []
    if term:
        suggestions = models.Recording.objects.filter(title__istartswith=term)[:3]
        ret = [{"category": "recordings", "name": l.title, 'mbid': str(l.mbid)} for i, l in enumerate(suggestions, 1)]
        suggestions = models.Artist.objects.filter(name__istartswith=term)[:3]
        ret += [{"category": "artists", "name": l.name, 'mbid': str(l.mbid)} for i, l in
                enumerate(suggestions, len(ret))]
    return HttpResponse(json.dumps(ret), content_type="application/json")


def recordings_search(request):
    q = request.GET.get('recording', '')

    s_artist = request.GET.get('composers', '')
    s_perf = request.GET.get('artists', '')
    s_form = request.GET.get('forms', '')
    s_makam = request.GET.get('makams', '')
    s_usul = request.GET.get('usuls', '')
    s_work = request.GET.get('works', '')

    recordings = models.Recording.objects
    next_page = None
    if s_work != '' or s_artist != '' or s_perf != '' or s_form != '' or s_usul != '' or s_makam != '' or q:
        recordings = get_works(s_work, s_artist, s_form, s_usul, s_makam, s_perf, q)

    paginator = Paginator(recordings.all(), 25)
    page = request.GET.get('page')
    try:
        recordings = paginator.page(page)
        if recordings.has_next():
            next_page = recordings.next_page_number()
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        recordings = paginator.page(1)
        if recordings.has_next():
            next_page = recordings.next_page_number()
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        recordings = paginator.page(paginator.num_pages)
    results = {
        'results': [item.get_dict() for item in recordings.object_list],
        "moreResults": next_page
    }
    return HttpResponse(json.dumps(results), content_type='application/json')


def get_works(work, artist, form, usul, makam, perf, q, elem=None):
    recordings = models.Recording.objects
    if q and q != '':
        ids = list(models.Work.objects.filter(title__unaccent__iexact=q).values_list('pk', flat=True))
        rel_ids = list(models.Release.objects.filter(title__unaccent__icontains=q).values_list('pk', flat=True))
        recordings = recordings.filter(works__id__in=ids) | recordings.filter(title__contains=q) | \
                     recordings.filter(release__id__in=rel_ids)

    if elem != "artist":
        if artist and artist != '':
            recordings = recordings.filter(works__composers__mbid__in=artist.split()) \
                         | recordings.filter(works__lyricists__mbid__in=artist.split())
    if elem != "form":
        if form and form != '':
            if form == '17':
                recordings = recordings.filter(has_gazel=True)
            if form == '67':
                recordings = recordings.filter(has_taksim=True)
            else:
                recordings = recordings.filter(works__form__uuid__in=form.split())
    if elem != "work":
        if work and work != '':
            recordings = recordings.filter(works__mbid__in=work.split())
    if elem != "usul":
        if usul and usul != '':
            recordings = recordings.filter(works__usul__uuid__in=usul.split())
    if elem != "makam":
        if makam and makam != '':
            recordings = recordings.filter(works__makam__uuid__in=makam.split())
    if elem != "performer":
        if perf and perf != '':
            recordings = recordings.filter(instrumentperformance__artist__mbid__in=perf.split()) | \
                         recordings.filter(release__artists__mbid__in=perf.split())

    recordings = recordings.distinct().order_by('title')
    return recordings


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
    urls["spectrogram"] = [("makamaudioimages", "inv_mfcc_spectrum8", 1, 0.3)]
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
        "tonicurl": [("jointanalysis", "tonic", 1, "0.1"),
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


def recordingbyid(request, recordingid, title=None):
    recording = get_object_or_404(models.Recording, pk=recordingid)
    return redirect(recording.get_absolute_url(), permanent=True)


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
                                                                           option[0], option[1], option[2],
                                                                           version=option[3])
                        ret[u] = success_content
                        break
                else:
                    success_content = docserver.util.docserver_get_url(mbid,
                                                                       option[0], option[1], option[2],
                                                                       version=option[3])
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
                                                                            'score', 'score', n + 1, '0.2'),
                                      '%s-%s-%d-%d' %
                                      ('score', 'score', n + 1, 2)))
            score = document[0].sourcefiles.filter(file_type__extension='xml')
            if len(score) == 1:
                filenames.append((score[0].fullpath, '%s-%s-%d-%d' %
                                  ('score', 'score', 1, 2)))
        try:
            filenames.append((docserver.util.docserver_get_filename(w.mbid,
                                                                    'scoreanalysis', 'metadata', 1, '0.1'),
                              '%s-%s-%d-%d' %
                              ('scoreanalysis', 'metadata', 1, 1)))
        except docserver.exceptions.NoFileException:
            pass

    keys = sorted(urls.keys(), reverse=True)
    for u in keys:
        for option in urls[u]:
            try:
                if option[0] in ('tomatodunya', 'makamaudioimages'):
                    filenames.append((docserver.util.docserver_get_filename(mbid, option[0],
                                                                            option[1], option[2], version=option[3]),
                                      '%s-%s-%d-%d' %
                                      (option[0], option[1], 1, int(float(option[3]) * 10))))
                    break
                content = docserver.util.docserver_get_json(mbid, option[0], option[1],
                                                            option[2], version=option[3])
                if content and (type(content) is list or
                                    (len(content.keys()) and
                                         ('pitch' in content or content[content.keys()[0]]))):
                    filenames.append((docserver.util.docserver_get_filename(mbid, option[0],
                                                                            option[1], option[2], version=option[3]),
                                      '%s-%s-%d-%d' %
                                      (option[0], option[1], 1, int(float(option[3]) * 10))))
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


def filters(request):
    makams = models.Makam.objects.prefetch_related('aliases').distinct()
    forms = models.Form.objects.prefetch_related('aliases').distinct()
    usuls = models.Usul.objects.prefetch_related('aliases').distinct()
    composers = models.Composer.objects.all()
    artists = models.Artist.objects.all()

    makamlist = []
    for r in makams:
        makamlist.append({"name": r.name, "uuid": str(r.uuid), "aliases": [a.name for a in r.aliases.all()]})

    formlist = []
    for r in forms:
        formlist.append({"name": r.name, "uuid": str(r.uuid), "aliases": [a.name for a in r.aliases.all()]})

    usullist = []
    for r in usuls:
        usullist.append({"name": r.name, "uuid": str(r.uuid), "aliases": [a.name for a in r.aliases.all()]})

    composerlist = []
    for r in composers:
        composerlist.append({"name": r.name, "mbid": str(r.mbid)})

    artistlist = []
    for a in artists:
        rr = []
        tt = []
        cc = []
        ii = []

        artistlist.append({"name": a.name, "mbid": str(a.mbid), "concerts": [str(c.mbid) for c in cc],
                           "raagas": [str(r.uuid) for r in rr], "taalas": [str(t.uuid) for t in tt],
                           "instruments": [str(i.mbid) for i in ii]})

    ret = {"artists": artistlist,
           "makams": makamlist,
           "forms": formlist,
           "usuls": usullist,
           "composers": composerlist,
           }

    return JsonResponse(ret)
