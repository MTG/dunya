# Copyright 2013,2014 Music Technology Group - Universitat Pompeu Fabra
# 
# This file is part of Dunya
# 
# Dunya is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation (FSF), either version 3 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/

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
            print "Artist", name, a.id
            a.gurus.clear()

            for g in guru.split(","):
                g = g.strip()
                try:
                    gobject = models.Artist.objects.get(name=g)
                    a.gurus.add(gobject)
                except models.Artist.DoesNotExist:
                    print "  * cannot find guru", g
                    print "  * making a dummy one"
                    gobject, created = models.Artist.objects.get_or_create(name=g, dummy=True)
                    a.gurus.add(gobject)

            try:
                gr = models.GeographicRegion.objects.get(name=place)
                a.state = gr
                a.save()
            except models.GeographicRegion.DoesNotExist:
                print "  * cannot find state", place

