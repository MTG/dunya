from django.core.management.base import BaseCommand, CommandError

from carnatic import models
from django.conf import settings
import pysolr
import intonation
import pypeaks

class Command(BaseCommand):
    help = 'Calculate recording similarity between recordings of the same raaga'
    solr = pysolr.Solr(settings.SOLR_URL)
    intonationmap = {}

    def make_search_data(self, data, etype, namefield):
        insert = {"id": "%s_%s" % (etype, i.pk),
                   "object_id_i": i.pk,
                   "type_s": etype,
                   "title_t": getattr(i, namefield),
                   "doctype_s": "recordingsimilarity"
                  }
        return insert

    def foo(self):
        self.solr.add(ret)
        self.solr.commit()

    def calculate_similarity(self):
        recordings = models.Recording.objects.all()
        for r in recordings:
            pitch = intonation.pitch.Pitch()
            rec = intonation.recording.Recording(pitch)
            # We calculated the histogram ourselves, so let's fake it
            rec.histogram = pypeaks.Data(hist, 256)
            raaga = recording.raaga()
            otherrecordings = models.Recording.objects.filter(work__raaga__in=[raaga]).exclude(pk=r.pk)

    def handle(self, *args, **options):
        self.calculate_similarity()
