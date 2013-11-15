import pysolr
from django.conf import settings
import collections

from carnatic import models

solr = pysolr.Solr(settings.SOLR_URL)
def search(name):
    name = name.lower()
    query = "title_t:%s" % name
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

