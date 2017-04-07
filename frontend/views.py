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
from django.http import JsonResponse
from django.db.models import Q

import carnatic

def main(request):
    return render(request, "frontend/index.html")

def filters(request):

    taalas = carnatic.models.Taala.objects.prefetch_related('aliases').all()
    taalalist = []
    for r in taalas:
        taalalist.append({"name": r.name, "uuid": str(r.uuid), "aliases": [a.name for a in r.aliases.all()]})

    raagas = carnatic.models.Raaga.objects.prefetch_related('aliases').all()
    raagalist = []
    for r in raagas:
        raagalist.append({"name": r.name, "uuid": str(r.uuid), "aliases": [a.name for a in r.aliases.all()]})

    concerts = carnatic.models.Concert.objects.all()
    concertlist = []
    for c in concerts:
        concertlist.append({"name": c.title, "mbid": str(c.mbid)})

    artists = carnatic.models.Artist.objects.all()
    artistlist = []
    for a in artists:
        #rr = carnatic.models.Raaga.objects.filter(Q(work__recording__concert__artists=a) | Q(work__recording__instrumentperformance__artist=a)).distinct()
        #tt = carnatic.models.Taala.objects.filter(Q(work__recording__concert__artists=a) | Q(work__recording__instrumentperformance__artist=a)).distinct()
        #cc = a.concerts()
        #ii = a.instruments()
        rr = []
        tt = []
        cc = []
        ii = []

        artistlist.append({"name": a.name, "mbid": str(a.mbid), "concerts": [str(c.mbid) for c in cc], "raagas": [str(r.uuid) for r in rr], "taalas": [str(t.uuid) for t in tt], "instruments": [str(i.mbid) for i in ii]})


    instruments = carnatic.models.Instrument.objects.all()
    instrumentlist = []
    for i in instruments:
        instrumentlist.append({"name": i.name, "mbid": str(i.mbid)})


    ret = {"artists": artistlist,
           "concerts": concertlist,
           "instruments": instrumentlist,
           u"ragas": raagalist,
           u"talas": taalalist,
           }

    return JsonResponse(ret)
