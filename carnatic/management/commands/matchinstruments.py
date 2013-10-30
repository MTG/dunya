from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile

import csv
import os
import re
from carnatic import models
from django.conf import settings
import data
import requests

class Command(BaseCommand):
    help = "Load ajay's updates to instruments"

    def handle(self, *args, **options):
        fname = args[0]

        #TODO: utf-8 in csv?
        reader = csv.reader(open(fname, "rb"))
        reader.next() # header
        for row in reader:
            name = row[0]
            percussion = row[2]
            wikipedia = row[4]
            picture = row[5]
            altpicture = row[6]
            altsource = row[7]
            source = row[8]
            description = row[9]

            i = models.Instrument.objects.get(name=name)
            i.is_percussion = not not percussion
            if not picture and altpicture:
                picture = altpicture
            if picture:
                req = requests.get(picture)
                piccontents = req.contents
                im = data.models.image()
                im.image.save("%s.jpg" % i.name, contentfile(piccontents))
                # TODO: Clear images
                i.images.remove()
                i.images.add(im)
                if source:
                    sn = data.models.SourceName.objects.get(name="kutcheris.com")
                    sourceob, created = data.models.Source.objects.get_or_create(source_name=sn, uri=link, defaults={"title": a.name})
                else:
                    sourceob = None
                descriptionob = data.models.Description.objects.create(description=description, source=sourceob)
                i.description = descriptionob
                i.save()



