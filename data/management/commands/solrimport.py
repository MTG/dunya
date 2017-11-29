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

import pysolr
from django.conf import settings
from django.core.management.base import BaseCommand

import carnatic.models
import hindustani.models
import makam.models


class Command(BaseCommand):
    help = 'Load data in the database to solr'
    solr_c = pysolr.Solr(settings.SOLR_URL + "/carnatic")
    solr_h = pysolr.Solr(settings.SOLR_URL + "/hindustani")
    solr_m = pysolr.Solr(settings.SOLR_URL + "/makam")

    def _create_document(self, elem, etype, namefield):
        doc = {"id": "%s_%s" % (etype, elem.pk),
               "object_id_i": elem.pk,
               "type_s": etype,
               "title_t": getattr(elem, namefield),
               "doctype_s": "search"
               }
        if hasattr(elem, "aliases"):
            aliases = []
            for a in elem.aliases.all():
                if hasattr(a, "name"):
                    aliases.append(a.name)
            if hasattr(elem, "common_name"):
                aliases.append(elem.common_name)
            if aliases:
                doc["alias_txt"] = aliases
        if hasattr(elem, "mbid"):
                doc["mbid_s"] = elem.mbid
        return doc

    def make_search_data(self, data, etype, namefield):
        insert = []
        for i in data:
            insert.append(self._create_document(i, etype, namefield))
        return insert

    def make_work_search_data(self, data):
        insert = []
        for i in data:
            doc = self._create_document(i, "composition", "title")
            doc["composer_s"] =  ", ".join([c.name for c in i.composerlist().all()])
            insert.append(doc)
        return insert

    def make_recording_search_data(self, data):
        insert = []
        for i in data:
            doc = self._create_document(i, "recording", "title")
            doc["artists_s"] = ", ".join([c.artist.name for c in i.instrumentperformance_set.all()])
            insert.append(doc)
        return insert

    def create_makam_search_index(self):
        print("Creating makam object index")

        works = makam.models.Work.objects.all()
        composers = makam.models.Composer.objects.filter(works__in=works).distinct()
        lyricists = makam.models.Composer.objects.filter(lyric_works__in=works.all()).distinct()
        artists = makam.models.Artist.objects.filter(instrumentperformance__recording__works__in=works).distinct() | \
                  makam.models.Artist.objects.filter(primary_concerts__recordings__works__in=works).distinct()

        makams = makam.models.Makam.objects.filter(work__in=works.all()).distinct()
        forms = makam.models.Form.objects.filter(work__in=works).distinct()
        usuls = makam.models.Usul.objects.filter(work__in=works).distinct()
        recordings = makam.models.Recording.objects.filter(works__in=works).distinct()

        insertcomposer = self.make_search_data(composers, "composer", "name")
        insertlyricist = self.make_search_data(lyricists, "lyricist", "name")
        insertartist = self.make_search_data(artists, "performer", "name")
        insertwork = self.make_work_search_data(works)
        insertmakam = self.make_search_data(makams, "makam", "name")
        insertform = self.make_search_data(forms, "form", "name")
        insertusul = self.make_search_data(usuls, "usul", "name")
        insertrecording = self.make_recording_search_data(recordings)

        self.solr_m.add(insertartist)
        self.solr_m.add(insertcomposer)
        self.solr_m.add(insertlyricist)
        self.solr_m.add(insertwork)
        self.solr_m.add(insertmakam)
        self.solr_m.add(insertform)
        self.solr_m.add(insertusul)
        self.solr_m.add(insertrecording)
        self.solr_m.commit()

    def create_carnatic_search_index(self):
        print("Creating carnatic object index")

        instruments = carnatic.models.Instrument.objects.all()
        artists = carnatic.models.Artist.objects.filter(dummy=False)
        composers = carnatic.models.Composer.objects.all()
        works = carnatic.models.Work.objects.all()
        concerts = carnatic.models.Concert.objects.all()
        raagas = carnatic.models.Raaga.objects.all()
        taalas = carnatic.models.Taala.objects.all()

        insertinstr = self.make_search_data(instruments, "instrument", "name")
        insertartist = self.make_search_data(artists, "artist", "name")
        insertcomposer = self.make_search_data(composers, "composer", "name")
        insertwork = self.make_search_data(works, "work", "title")
        insertconcert = self.make_search_data(concerts, "concert", "title")
        insertraaga = self.make_search_data(raagas, "raaga", "name")
        inserttaala = self.make_search_data(taalas, "taala", "name")

        self.solr_c.add(insertinstr)
        self.solr_c.add(insertartist)
        self.solr_c.add(insertcomposer)
        self.solr_c.add(insertwork)
        self.solr_c.add(insertconcert)
        self.solr_c.add(insertraaga)
        self.solr_c.add(inserttaala)
        self.solr_c.commit()

    def create_hindustani_search_index(self):
        print("Creating hindustani object index")

        instruments = hindustani.models.Instrument.objects.all()
        artists = hindustani.models.Artist.objects.filter(dummy=False)
        composers = hindustani.models.Composer.objects.all()
        works = hindustani.models.Work.objects.all()
        releases = hindustani.models.Release.objects.all()
        raags = hindustani.models.Raag.objects.all()
        taals = hindustani.models.Taal.objects.all()
        forms = hindustani.models.Form.objects.all()
        layas = hindustani.models.Laya.objects.all()

        insertinstr = self.make_search_data(instruments, "instrument", "name")
        insertartist = self.make_search_data(artists, "artist", "name")
        insertcomposer = self.make_search_data(composers, "composer", "name")
        insertwork = self.make_search_data(works, "work", "title")
        insertrelease = self.make_search_data(releases, "release", "title")
        insertraag = self.make_search_data(raags, "raag", "common_name")
        inserttaal = self.make_search_data(taals, "taal", "common_name")
        insertform = self.make_search_data(forms, "form", "common_name")
        insertlaya = self.make_search_data(layas, "laya", "common_name")

        self.solr_h.add(insertinstr)
        self.solr_h.add(insertartist)
        self.solr_h.add(insertcomposer)
        self.solr_h.add(insertwork)
        self.solr_h.add(insertrelease)
        self.solr_h.add(insertraag)
        self.solr_h.add(inserttaal)
        self.solr_h.add(insertform)
        self.solr_h.add(insertlaya)
        self.solr_h.commit()

    def create_carnatic_concert_index(self):
        print("Creating carnatic concert index")
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
                for w in t.works.all():
                    works.append(w.id)
                for ra in t.raagas.all():
                    raagas.append(ra.id)
                for ta in t.taalas.all():
                    taalas.append(ta.id)

            ret.append({"doctype_s": "concertsimilar",
                        "id": "concertsimilar_%s" % c.id,
                        "concertid_i": c.id,
                        "raaga_is": raagas,
                        "taala_is": taalas,
                        "work_is": works,
                        "artist_is": artists,
                        })
        self.solr_c.add(ret)
        self.solr_c.commit()

    def create_hindustani_release_index(self):
        print("Creating hindustani release index")

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
                        })
        self.solr_h.add(ret)
        self.solr_h.commit()

    def handle(self, *args, **options):
        self.create_makam_search_index()

        self.create_carnatic_search_index()
        self.create_carnatic_concert_index()

        self.create_hindustani_search_index()
        self.create_hindustani_release_index()
