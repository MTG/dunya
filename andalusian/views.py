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
import json

from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from andalusian import models
import docserver

def search(request):
    q = request.GET.get('recording', '')
    s_mizan = request.GET.get('mizans', '')
    s_nawba = request.GET.get('nawbas', '')

    recordings = models.Recording.objects
    if q and q!='':
        ids = list(models.Work.objects.filter(title__icontains=q).values_list('pk', flat=True))
        recordings = recordings.filter(works__id__in=ids)\
                | recordings.filter(title__icontains=q)\
                | recordings.filter(concert__title__icontains=q)
    if s_nawba and s_nawba != '':
        recordings = recordings.filter(section__nawba=s_nawba)
    if s_mizan and s_mizan != '':
        recordings = recordings.filter(section__mizan=s_mizan)

    paginator = Paginator(recordings.all(), 25)
    page = request.GET.get('page')
    next_page = None
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
            "results": [item.get_dict() for item in recordings.object_list],
            "moreResults": next_page
    }
    return HttpResponse(json.dumps(results), content_type='application/json')


def searchcomplete(request):
    term = request.GET.get("input")
    ret = []
    if term:
        suggestions = models.Recording.objects.filter(title__istartswith=term)[:3]
        ret = [{"category": "recordings", "name": l.title, 'mbid': str(l.mbid)} for i, l in enumerate(suggestions, 1)]
        suggestions = models.Artist.objects.filter(name__istartswith=term)[:3]
        ret += [{"category": "artists", "name": l.name, 'mbid': str(l.mbid)} for i, l in enumerate(suggestions, len(ret))]
    return HttpResponse(json.dumps(ret), content_type="application/json")


def recordingbyid(request, recordingid, title=None):
    recording = get_object_or_404(models.Recording, pk=recordingid)
    return redirect(recording.get_absolute_url(), permanent=True)


def recording(request, uuid, title=None):
    recording = get_object_or_404(models.Recording, mbid=uuid)

    try:
        audio = docserver.util.docserver_get_mp3_url(uuid)
    except docserver.exceptions.NoFileException:
        audio = None

    try:
        score = docserver.util.docserver_get_url(uuid, "svgscore", "score", 1, version=0.1)
    except docserver.exceptions.NoFileException:
        score = None

    try:
        smallimage = docserver.util.docserver_get_url(uuid, "smallaudioimages", "smallfull", 1, version=0.1)
    except docserver.exceptions.NoFileException:
        smallimage = None


    ret={
         "recording": recording,
         "audio": audio,
         "scoreurl": score,
         "smallimageurl": smallimage,
        }
    return render(request, "andalusian/recording.html", ret)


def filters(request):

    mizans = models.Mizan.objects.all()
    nawbas = models.Nawba.objects.all()
    artists = models.Artist.objects.all()

    mizanlist = []
    for r in mizans:
        mizanlist.append({"name": r.name, "uuid": str(r.id), "aliases": []})

    nawbalist = []
    for r in nawbas:
        nawbalist.append({"name": r.name, "uuid": str(r.id), "aliases": []})

    artistlist = []
    for a in artists:
        rr = []
        tt = []
        cc = []
        ii = []

        artistlist.append({"name": a.name, "mbid": str(a.mbid), })


    ret = {"artists": artistlist,
           "nawbas": nawbalist,
           "mizans": mizanlist,
           }

    return JsonResponse(ret)


