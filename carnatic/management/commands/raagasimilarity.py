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

from __future__ import print_function

import collections
import decimal
import json

import compmusic.extractors.similaritylib.raaga
import numpy as np
import os
import pysolr
from compmusic.extractors.similaritylib import recording
from django.conf import settings
from django.core.management.base import BaseCommand
from scipy.ndimage.filters import gaussian_filter

import carnatic
import hindustani
from docserver import util


class Command(BaseCommand):
    help = 'Calculate distance between mean raaga profiles'
    solr = pysolr.Solr(settings.SOLR_URL)
    intonationmap = {}
    distancemap = {}
    dirname = "raagasimilarity-%s"

    def make_data(self, obj, module):
        mbid = obj["mbid"]
        sim = obj["similar"]
        if not sim:
            return None
        insert = {"id": "raagasim_%s" % (mbid, ),
                  "similar_s": json.dumps(sim),
                  "rid_t": mbid,
                  "doctype_s": "raagasimilarity",
                  "module_s": module
                  }
        return insert

    def import_solr(self, module):
        dirname = self.dirname % module
        files = os.listdir(dirname)
        ret = []
        for f in files:
            path = os.path.join(dirname, f)
            data = json.load(open(path))
            val = self.make_data(data, module)
            if val:
                ret.append(val)
        self.solr.add(ret)
        self.solr.commit()

    def compute_similarity(self, raag, raagprofile, otherraags, module):
        rid = raag.pk
        dirname = self.dirname % module
        try:
            os.makedirs(dirname)
        except OSError:
            pass
        sims = []
        for oraag, oprofile in otherraags.items():
            oid = oraag.pk

            if (rid, oid) in self.distancemap:
                # print " -hit d-ab"
                distance = self.distancemap[(rid, oid)]
            elif (oid, rid) in self.distancemap:
                # print " -hit d-ba"
                distance = self.distancemap[(oid, rid)]
            else:
                distance = recording.kldiv(raagprofile, oprofile)
                self.distancemap[(rid, oid)] = distance
            print("distance between %s-%s is %s" % (rid, oid, distance))

            if distance:
                sims.append((oid, distance))
        sims = [ (i[0], round(i[1], 2)) for i in sims if not decimal.Decimal(i[1]).is_nan() ]
        sims = sorted(sims, key=lambda a: a[1])
        name = os.path.join(dirname, "%s.json" % rid)
        ret = {"rid": rid, "similar": sims}
        json.dump(ret, open(name, "wb"), indent=2)

    def calc_profile(self, raag, recordings):
        average = compmusic.extractors.similaritylib.raaga.Raaga(raag.name, "")
        pitches = []
        tonics = []
        for r in recordings:
            mbid = r.mbid
            try:
                pitch = util.docserver_get_json(mbid, "pitch", "pitch")
                tonic = util.docserver_get_contents(mbid, "votedtonic", "tonic")
                try:
                    tonic = float(tonic)
                    npp = np.array(pitch)
                    pitches.append(npp)
                    tonics.append(tonic)
                except ValueError:
                    pass
            except util.NoFileException:
                pass
        average.compute_average_hist_data(pitches, tonics)
        profile = average.average_hist[:, 0]
        y = np.concatenate((profile[-50:], profile[:-50]))
        y = gaussian_filter(y, 7)
        return y.tolist()

    def compute_matrix_carnatic(self):
        recordings = carnatic.models.Recording.objects.filter(concert__collection__permission__in=['R', 'U'])
        recmap = collections.defaultdict(list)
        for r in recordings:
            ra = r.get_raaga()
            if ra and ra[0]:
                recmap[ra[0]].append(r)
        numraagas = len(recmap.keys())
        print("Got", numraagas, "raags")
        raagaprofiles = {}
        for i, (raag, recordings) in enumerate(recmap.items(), 1):
            print("(%s/%s) %s" % (i, numraagas, raag))
            profile = self.calc_profile(raag, recordings)
            raagaprofiles[raag] = profile

        for r, profile in raagaprofiles.items():
            # We make a copy of the profiles so that we can delete
            # the "current" one and use the remainder to compare with
            otherraags = raagaprofiles.copy()
            del otherraags[r]
            self.compute_similarity(r, profile, otherraags, "carnatic")

    def compute_matrix_hindustani(self):
        print("Creating hindustani raag images")
        recordings = hindustani.models.Recording.objects.all()
        recmap = collections.defaultdict(list)
        for r in recordings:
            if r.raags.count() == 1:
                raag = r.raags.get()
                recmap[raag].append(r)
        numraagas = len(recmap.keys())
        print("Got %s raags" % numraagas)
        raagaprofiles = {}
        for i, (raag, recordings) in enumerate(recmap.items(), 1):
            print("(%s/%s) %s" % (i, numraagas, raag))
            profile = self.calc_profile(raag, recordings)
            raagaprofiles[raag] = profile

        for r, profile in raagaprofiles.items():
            # We make a copy of the profiles so that we can delete
            # the "current" one and use the remainder to compare with
            otherraags = raagaprofiles.copy()
            del otherraags[r]
            self.compute_similarity(r, profile, otherraags, "hindustani")

    def handle(self, *args, **options):
        self.compute_matrix_carnatic()
