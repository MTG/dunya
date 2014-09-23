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

from django.core.management.base import BaseCommand

import carnatic
import hindustani

from django.conf import settings
import pysolr

class Command(BaseCommand):
    help = 'Load data in the database to solr'
    solr = pysolr.Solr(settings.SOLR_URL)

    def make_search_data(self, module, data, etype, namefield):
        insert = []
        for i in data:
            doc = {"id": "%s_%s" % (etype, i.pk),
                   "object_id_i": i.pk,
                   "type_s": etype,
                   "module_s": module,
                   "title_t": getattr(i, namefield),
                   "doctype_s": "search"
                   }
            if hasattr(i, "aliases"):
                aliases = []
                for a in i.aliases.all():
                    if hasattr(a, "name"):
                        aliases.append(a.name)
                if hasattr(i, "common_name"):
                    aliases.append(i.common_name)
                if aliases:
                    doc["alias_txt"] = aliases
            if hasattr(i, "bootleg"):
                doc["bootleg_s"] = i.bootleg
            insert.append(doc)
        return insert

    def create_carnatic_search_index(self):
        print "Creating carnatic object index"

        instruments = carnatic.models.Instrument.objects.all()
        artists = carnatic.models.Artist.objects.filter(dummy=False)
        composers = carnatic.models.Composer.objects.all()
        works = carnatic.models.Work.objects.all()
        concerts = carnatic.models.Concert.objects.all()
        raagas = carnatic.models.Raaga.objects.all()
        taalas = carnatic.models.Taala.objects.all()

        insertinstr = self.make_search_data("carnatic", instruments, "instrument", "name")
        insertartist = self.make_search_data("carnatic", artists, "artist", "name")
        insertcomposer = self.make_search_data("carnatic", composers, "composer", "name")
        insertwork = self.make_search_data("carnatic", works, "work", "title")
        insertconcert = self.make_search_data("carnatic", concerts, "concert", "title")
        insertraaga = self.make_search_data("carnatic", raagas, "raaga", "name")
        inserttaala = self.make_search_data("carnatic", taalas, "taala", "name")

        self.solr.add(insertinstr)
        self.solr.add(insertartist)
        self.solr.add(insertcomposer)
        self.solr.add(insertwork)
        self.solr.add(insertconcert)
        self.solr.add(insertraaga)
        self.solr.add(inserttaala)
        self.solr.commit()

    def create_hindustani_search_index(self):
        print "Creating hindustani object index"

        instruments = hindustani.models.Instrument.objects.all()
        artists = hindustani.models.Artist.objects.filter(dummy=False)
        composers = hindustani.models.Composer.objects.all()
        works = hindustani.models.Work.objects.all()
        releases = hindustani.models.Release.objects.all()
        raags = hindustani.models.Raag.objects.all()
        taals = hindustani.models.Taal.objects.all()
        forms = hindustani.models.Form.objects.all()
        layas = hindustani.models.Laya.objects.all()

        insertinstr = self.make_search_data("hindustani", instruments, "instrument", "name")
        insertartist = self.make_search_data("hindustani", artists, "artist", "name")
        insertcomposer = self.make_search_data("hindustani", composers, "composer", "name")
        insertwork = self.make_search_data("hindustani", works, "work", "title")
        insertrelease = self.make_search_data("hindustani", releases, "release", "title")
        insertraag = self.make_search_data("hindustani", raags, "raag", "common_name")
        inserttaal = self.make_search_data("hindustani", taals, "taal", "common_name")
        insertform = self.make_search_data("hindustani", forms, "form", "common_name")
        insertlaya = self.make_search_data("hindustani", layas, "laya", "common_name")

        self.solr.add(insertinstr)
        self.solr.add(insertartist)
        self.solr.add(insertcomposer)
        self.solr.add(insertwork)
        self.solr.add(insertrelease)
        self.solr.add(insertraag)
        self.solr.add(inserttaal)
        self.solr.add(insertform)
        self.solr.add(insertlaya)
        self.solr.commit()

    def create_carnatic_concert_index(self):
        print "Creating carnatic concert index"
        concerts = carnatic.models.Concert.objects.all()
        ret = []
        for c in concerts:
            raagas = []  # list of (rid, rname)
            taalas = []
            works = []
            artists = []
            for a in c.artists.all():
                artists.append(a.id)
            for a in c.performers():
                artists.append(a.id)
            for t in c.recordings.all():
                if t.work:
                    works.append(t.work.id)
                    for ra in t.work.raaga.all():
                        raagas.append(ra.id)
                    for ta in t.work.taala.all():
                        taalas.append(ta.id)

            ret.append({"doctype_s": "concertsimilar",
                        "id": "concertsimilar_%s" % c.id,
                        "concertid_i": c.id,
                        "raaga_is": raagas,
                        "taala_is": taalas,
                        "work_is": works,
                        "artist_is": artists,
                        "module_s": "carnatic"
                        })
        self.solr.add(ret)
        self.solr.commit()

    def create_hindustani_release_index(self):
        print "Creating hindustani release index"

        releases = hindustani.models.Release.objects.all()
        ret = []
        for r in releases:
            raags = []  # list of (rid, rname)
            taals = []
            forms = []
            layas = []
            works = []
            artists = []
            for a in r.artists.all():
                artists.append(a.id)
            for p in r.performers():
                artists.append(p.id)
            artists = list(set(artists))
            for t in r.recordings.all():
                for w in t.works.all():
                    works.append(w.id)

                for ra in t.raags.all():
                    raags.append(ra.id)
                for ta in t.taals.all():
                    taals.append(ta.id)
                for fo in t.forms.all():
                    forms.append(fo.id)
                for la in t.layas.all():
                    layas.append(la.id)

            ret.append({"doctype_s": "releasesimilar",
                        "id": "releasesimilar_%s" % r.id,
                        "releaseid_i": r.id,
                        "raag_is": raags,
                        "taal_is": taals,
                        "form_is": forms,
                        "laya_is": layas,
                        "work_is": works,
                        "artist_is": artists,
                        "module_s": "hindustani",
                        })
        self.solr.add(ret)
        self.solr.commit()

    def handle(self, *args, **options):
        self.create_carnatic_search_index()
        self.create_carnatic_concert_index()

        self.create_hindustani_search_index()
        self.create_hindustani_release_index()
