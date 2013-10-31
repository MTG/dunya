from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile

import csv
import os
import re
from carnatic import models
from django.conf import settings
import data
import requests

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

class Command(BaseCommand):
    help = "Load ajay's updates to instruments"

    def handle(self, *args, **options):
        fname = args[0]

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
            description = row[9].decode("utf-8")

            print name

            i = models.Instrument.objects.get(name=name)
            i.percussion = not not percussion
            if not picture and altpicture:
                picture = altpicture
            if picture:
                print "downloading picture from", picture
                req = requests.get(picture)
                piccontents = req.content
                im = data.models.Image()
                i.images.remove()
                im.image.save("%s.jpg" % i.name, ContentFile(piccontents))
                i.images.add(im)
            if description:
                if source:
                    sn = data.models.SourceName.objects.get(name="Wikipedia")
                    sourceob, created = data.models.Source.objects.get_or_create(source_name=sn, uri=source, defaults={"title": name})
                else:
                    sourceob = None
                descriptionob = data.models.Description.objects.create(description=description, source=sourceob)
                i.description = descriptionob
            i.save()

