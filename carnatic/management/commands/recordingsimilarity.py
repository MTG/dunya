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

from django.core.management.base import BaseCommand, CommandError

from carnatic import models
from django.conf import settings
import pysolr
import json
import os

from compmusic.extractors.similaritylib import recording
from docserver import util
import docserver

class Command(BaseCommand):
    help = 'Calculate recording similarity between recordings of the same raaga'
    solr = pysolr.Solr(settings.SOLR_URL)
    intonationmap = {}
    distancemap = {}

    def make_data(self, obj):
        mbid = obj["mbid"]
        sim = obj["similar"]
        if not sim:
            return None
        insert = {"id": "sim_%s" % (mbid, ),
                   "similar_s": json.dumps(sim),
                   "mbid_t": mbid,
                   "doctype_s": "recordingsimilarity"
                  }
        return insert

    def import_solr(self):
        files = os.listdir("similarity")
        ret = []
        for f in files:
            path = os.path.join("similarity", f)
            data = json.load(open(path))
            val = self.make_data(data)
            if val:
                ret.append(val)
        self.solr.add(ret)
        self.solr.commit()

    def compute_distance(self, a, b):
        if a in self.intonationmap:
            #print " -hit a"
            adata = self.intonationmap[a]
        else:
            try:
                adata = util.docserver_get_json(a, "normalisedpitch", "normalisedhistogram")
            except docserver.models.Document.DoesNotExist:
                return None
            self.intonationmap[a] = adata
        if b in self.intonationmap:
            #print " -hit b"
            bdata = self.intonationmap[b]
        else:
            try:
                bdata = util.docserver_get_json(b, "normalisedpitch", "normalisedhistogram")
            except docserver.models.Document.DoesNotExist:
                return None
            self.intonationmap[b] = bdata

        if (a, b) in self.distancemap:
            #print " -hit d-ab"
            distance = self.distancemap[(a, b)]
        elif (b, a) in self.distancemap:
            #print " -hit d-ba"
            distance = self.distancemap[(b, a)]
        else:
            distance = recording.kldiv(adata, bdata)
            self.distancemap[(a, b)] = distance
        return distance

    def compute_similarity(self, rec):
        raaga = rec.raaga()
        otherrecordings = models.Recording.objects.filter(work__raaga__in=[raaga]).exclude(pk=rec.pk)
        rid = rec.mbid
        try:
            os.makedirs("similarity")
        except OSError:
            pass
        sims = []
        for o in otherrecordings:
            oid = o.mbid
            distance = self.compute_distance(rid, oid)
            if distance:
                sims.append((oid, distance))
        sims = sorted(sims, key=lambda a: a[1], reverse=True)
        name = "similarity/%s.json" % rid
        ret = {"mbid": rid, "similar": sims}
        json.dump(ret, open(name, "wb"))

    def compute_matrix(self):
        recordings = models.Recording.objects.all()
        total = len(recordings)
        for i, r in enumerate(recordings, 1):
            print "Recording %s (%s/%s)" % (r, i, total)
            self.compute_similarity(r)

    def handle(self, *args, **options):
        if len(args) and args[0] == "import":
            print "importing"
            self.import_solr()
        else:
            self.compute_matrix()
