from django.core.management.base import BaseCommand, CommandError

from carnatic import models
from dashboard import external_data

class Command(BaseCommand):
    help = 'Load descriptions and images for carnatic instruments'

    def handle(self, *args, **options):
        instruments = models.Instrument.objects.all()
        for i in instruments:
            print "Loading instrument data for", i
            external_data.import_instrument_description(i) 
