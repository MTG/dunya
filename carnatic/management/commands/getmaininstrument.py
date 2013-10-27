from django.core.management.base import BaseCommand, CommandError

from carnatic import models
import collections

class Command(BaseCommand):
    help = "Find each artist's main instrument and fill in the field"

    def handle(self, *args, **options):
        artists = models.Artist.objects.all()
        for a in artists:
            counter = collections.Counter()
            for ip in a.instrumentperformance_set.all():
                counter[ip.instrument] += 1
            for ip in a.instrumentconcertperformance_set.all():
                counter[ip.instrument] += 1
            try:
                common = counter.most_common(1)[0]
                inst = common[0]
                a.main_instrument = inst
                a.save()
            except IndexError:
                pass


