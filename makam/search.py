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

import collections
import json

import pysolr
from django.conf import settings

import makam.models

solr = pysolr.Solr(settings.SOLR_URL + "/makam")


def search(name, with_restricted=False):
    name = name.lower()
    query = "doctype_s:search AND title_t:(%s)" % name
    results = solr.search(query, rows=100)
    ret = collections.defaultdict(list)
    for d in results.docs:
        type = d["type_s"]
        id = d["object_id_i"]
        id = int(id)
        klass = get_klassmap().get(type)
        if klass:
            try:
                instance = klass.objects.get(pk=id)
                if type == "release":
                    if with_restricted or (instance.collection and instance.collection.permission != "S"):
                        ret[type].append(instance)
                elif type != "release":
                    ret[type].append(instance)
            except klass.DoesNotExist:
                pass
    return dict(ret)


def autocomplete(term):
    params = {}
    params['wt'] = 'json'
    params['q'] = term
    params['fl'] = "title_t,type_s,object_id_i,mbid_s,artists_s,composer_s"
    path = 'suggest/?%s' % pysolr.safe_urlencode(params, True)
    response = solr._send_request('get', path)
    res = json.loads(response)
    check = res.get("response", {})
    docs = check.get("docs", [])
    ret = []
    return docs


def get_klassmap():
    return {"instrument": makam.models.Instrument,
            "makam": makam.models.Makam,
            "form": makam.models.Form,
            "usul": makam.models.Usul,
            "release": makam.models.Release,
            "artist": makam.models.Artist,
            "work": makam.models.Work,
            "composer": makam.models.Composer}
