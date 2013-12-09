from django.core.management.base import BaseCommand, CommandError

from carnatic import models
from django.conf import settings
import pysolr

class Command(BaseCommand):
    help = 'Load data in the database to solr'
    solr = pysolr.Solr(settings.SOLR_URL)

    def handle(self, *args, **options):
        self.solr.delete(q="*:*")
        self.solr.commit()

