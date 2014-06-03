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

import pysolr
from django.conf import settings
import collections
import json

import hindustani

solr = pysolr.Solr(settings.SOLR_URL)
def search(name):
    name = name.lower()
    query = "module_s:hindustani AND doctype_s:search AND title_t:(%s)" % name
    results = solr.search(query, rows=100)
    ret = collections.defaultdict(list)
    klass_map = {"instrument": hindustani.models.Instrument,
                 "raag": hindustani.models.Raag,
                 "taal": hindustani.models.Taal,
                 "laya": hindustani.models.Laya,
                 "form": hindustani.models.Form,
                 "release": hindustani.models.Release,
                 "artist": hindustani.models.Artist,
                 "work": hindustani.models.Work,
                 "composer": hindustani.models.Composer}
    for d in results.docs:
        type = d["type_s"]
        id = d["object_id_i"]
        id = int(id)
        klass = klass_map.get(type)
        if klass:
            instance = klass.objects.get(pk=id)
            ret[type].append(instance)
    return ret

def autocomplete(term):
    params = {}
    params['wt'] = 'json'
    params['q'] = term
    params['fq'] = "module_s:hindustani"
    path = 'suggest/?%s' % pysolr.safe_urlencode(params, True)
    response = solr._send_request('get', path)
    res = json.loads(response)
    check = res.get("spellcheck", {})
    suggs = check.get("suggestions", [])
    if term in suggs:
        index = suggs.index(term) + 1
        if index < len(suggs):
            suggestions = suggs[index].get("suggestion", [])
            return suggestions
    return []

def get_similar_releases(artists, raags, taals, layas):
    artistids = set(artists)
    raagids = set(raags)
    taalids = set(taals)
    layaids = set(layas)
    artists = " ".join(map(str, artistids))
    raags = " ".join(map(str, raagids))
    taals = " ".join(map(str, taalids))
    layas = " ".join(map(str, layaids))

    searchitems = []
    if artists:
        searchitems.append("artist_is:(%s)" % artists)
    if taals:
        searchitems.append("taal_is:(%s)" % taals)
    if raags:
        searchitems.append("raag_is:(%s)" % raags)
    if layas:
        searchitems.append("laya_is:(%s)" % layas)

    if not searchitems:
        # If we have nothing to search for, return no matches
        return []

    query = "module_s:hindustani AND doctype_s:releasesimilar AND (%s)" % (" ".join(searchitems), )
    results = solr.search(query, rows=100)

    ret = []
    for d in results.docs:
        concertid = d["releaseid_i"]
        da = set(d.get("artist_is", []))
        dr = set(d.get("raag_is", []))
        dt = set(d.get("taal_is", []))
        dl = set(d.get("laya_is", []))
        commona = list(artistids & da)
        commonr = list(raagids & dr)
        commont = list(taalids & dt)
        commonl = list(layaids & dl)

        ret.append((concertid, {"raags": commonr, "taals": commont, "artists": commona, "layas": commonl}))
    return ret

