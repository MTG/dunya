from django.core.management.base import BaseCommand, CommandError

from carnatic import models
from django.conf import settings
import pysolr

class Command(BaseCommand):
    help = 'Load data in the database to solr'
    solr = pysolr.Solr(settings.SOLR_URL)

    def make_data(self, data, etype, namefield):
        insert = [{"id": "%s_%s" % (etype, i.pk),
                   "object_id_i": i.pk,
                   "type_s": etype,
                   "title_t": getattr(i, namefield)
                  } for i in data]
        return insert

    def handle(self, *args, **options):
        instruments = models.Instrument.objects.all()
        artists = models.Artist.objects.all()
        composers = models.Composer.objects.all()
        works = models.Work.objects.all()
        concerts = models.Concert.objects.all()
        raagas = models.Raaga.objects.all()
        taalas = models.Taala.objects.all()

        insertinstr = self.make_data(instruments, "instrument", "name")
        insertartist = self.make_data(artists, "artist", "name")
        insertcomposer = self.make_data(composers, "composer", "name")
        insertwork = self.make_data(works, "work", "title")
        insertconcert = self.make_data(concerts, "concert", "title")
        insertraaga = self.make_data(raagas, "raaga", "name")
        inserttaala = self.make_data(taalas, "taala", "name")

        self.solr.add(insertinstr)
        self.solr.add(insertartist)
        self.solr.add(insertcomposer)
        self.solr.add(insertwork)
        self.solr.add(insertconcert)
        self.solr.add(insertraaga)
        self.solr.add(inserttaala)
        self.solr.commit()

