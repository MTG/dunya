from django.core.management.base import BaseCommand, CommandError

from carnatic import models
from django.conf import settings
import pysolr

class Command(BaseCommand):
    help = 'Load data in the database to solr'
    solr = pysolr.Solr(settings.SOLR_URL)

    def make_search_data(self, data, etype, namefield):
        insert = [{"id": "%s_%s" % (etype, i.pk),
                   "object_id_i": i.pk,
                   "type_s": etype,
                   "title_t": getattr(i, namefield),
                   "doctype_s": "search"
                  } for i in data]
        return insert

    def create_search_index(self):
        instruments = models.Instrument.objects.all()
        artists = models.Artist.objects.all()
        composers = models.Composer.objects.all()
        works = models.Work.objects.all()
        concerts = models.Concert.objects.all()
        raagas = models.Raaga.objects.all()
        taalas = models.Taala.objects.all()

        insertinstr = self.make_search_data(instruments, "instrument", "name")
        insertartist = self.make_search_data(artists, "artist", "name")
        insertcomposer = self.make_search_data(composers, "composer", "name")
        insertwork = self.make_search_data(works, "work", "title")
        insertconcert = self.make_search_data(concerts, "concert", "title")
        insertraaga = self.make_search_data(raagas, "raaga", "name")
        inserttaala = self.make_search_data(taalas, "taala", "name")

        self.solr.add(insertinstr)
        self.solr.add(insertartist)
        self.solr.add(insertcomposer)
        self.solr.add(insertwork)
        self.solr.add(insertconcert)
        self.solr.add(insertraaga)
        self.solr.add(inserttaala)
        self.solr.commit()

    def create_concert_index(self):
        # TODO: Hindustani might have more than 1 raaga or taala
        concerts = models.Concert.objects.all()
        ret = []
        for c in concerts:
            raagas = [] # list of (rid, rname)
            taalas = []
            works = []
            artists = []
            for a in c.artists.all():
                artists.append(a.id)
            for p in c.performers():
                artists.append(p.performer.id)
            for t in c.tracks.all():
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
                        "artist_is": artists
                       })
        self.solr.add(ret)
        self.solr.commit()

    def handle(self, *args, **options):
        self.create_search_index()
        self.create_concert_index()

