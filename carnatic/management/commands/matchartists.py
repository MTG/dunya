from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile

import csv
import os
import re
from carnatic import models
from django.conf import settings
import data

class Command(BaseCommand):
    help = "Load vignesh's updates to artists"
    options = 'artistsheet'

    def handle(self, *args, **options):
        fname = args[0]

        reader = csv.DictReader(open(fname, "rb"))
        for row in reader:
            id = row["ID"]
            guru = row["Guru"]
            name = row["Name"]
            place = row["Region of Birth"]

            if not guru:
                continue

            a = models.Artist.objects.get(pk=int(id))
            print "Artist", name

            for g in guru.split(","):
                g = g.strip()
                try:
                    gobject = models.Artist.objects.get(name=g)
                    a.gurus.add(gobject)
                except models.Artist.DoesNotExist:
                    print "  * cannot find guru", g
            try:
                gr = models.GeographicRegion.objects.get(name=place)
                a.state = gr
                a.save()
            except models.GeographicRegion.DoesNotExist:
                print "  * cannot find state", place

