from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile

from carnatic import models
from django.conf import settings

from PIL import Image
import os
import cStringIO

class Command(BaseCommand):
    help = 'Make mini versions of all images that are loaded'

    def make_small(self, item):
        print item
        size = 150, 150
        for img in item.images.all():
            print "  ", img
            big = img.image
            fname = os.path.basename(big.name)
            smallfname = "small_%s" % fname
            try:
                pilimage = Image.open(big.path)
                out = cStringIO.StringIO()
                pilimage.thumbnail(size)
                pilimage.save(out, "JPEG")

                img.small_image.save(smallfname, ContentFile(out.getvalue()))
                img.save()
            except IOError:
                pass

    def handle(self, *args, **options):
        instruments = models.Instrument.objects.all()
        for i in instruments:
            self.make_small(i)

        artists = models.Artist.objects.all()
        for a in artists:
            self.make_small(a)

        composers = models.Composer.objects.all()
        for c in composers:
            self.make_small(c)

        concerts = models.Concert.objects.all()
        for c in concerts:
            self.make_small(c)

        raagas = models.Raaga.objects.all()
        for r in raagas:
            self.make_small(r)

        taalas = models.Taala.objects.all()
        for t in taalas:
            self.make_small(t)

