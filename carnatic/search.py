import pysolr
from django.conf import settings
import collections
import json

#from carnatic import models

solr = pysolr.Solr(settings.SOLR_URL)
def search(name):
    name = name.lower()
    query = "doctype_s:search AND title_t:(%s)" % name
    results = solr.search(query, rows=100)
    ret = collections.defaultdict(list)
    klass_map = {"instrument": models.Instrument,
                 "raaga": models.Raaga,
                 "taala": models.Taala,
                 "concert": models.Concert,
                 "artist": models.Artist,
                 "work": models.Work,
                 "composer": models.Composer}
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
    # specify json encoding of results
    params = {}
    params['wt'] = 'json'
    params['q'] = term
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

def get_concerts_with_raagas(raagas):
    if not isinstance(raagas, list):
        raagas = [raagas]
    raagas = " ".join(raagas)
    query = "doctype_s:concertsimilar AND raaga_is:(%s)" % raagas
    results = solr.search(query, rows=100)
    ret = []
    for d in results.docs:
        concertid = d["concertid_i"]
        ret.append(models.Concert.objects.get(pk=concertid))
    return ret

def get_similar_concerts(works, raagas, taalas, artists):
    workids = set(works)
    raagaids = set(raagas)
    taalaids = set(taalas)
    artistids = set(artists)
    raagas = " ".join(map(str, raagaids))
    taalas = " ".join(map(str, taalaids))
    works = " ".join(map(str, workids))
    artists = " ".join(map(str, artistids))

    query = "doctype_s:concertsimilar AND (taala_is:(%s) raaga_is:(%s) work_is:(%s) artist_is:(%s))" % (taalas, raagas, works, artists)
    results = solr.search(query, rows=100)

    ret = []
    for d in results.docs:
        concertid = d["concertid_i"]
        dr = set(d.get("raaga_is", []))
        dt = set(d.get("taala_is", []))
        dw = set(d.get("work_is", []))
        da = set(d.get("artist_is", []))
        commonr = list(raagaids & dr)
        commont = list(taalaids & dt)
        commona = list(artistids & da)
        commonw = list(workids & dw)

        ret.append((concertid, {"works": commonw, "raagas": commonr, "taalas": commont, "artists": commona}))
    return ret
