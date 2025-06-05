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


import csv

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

import data
from carnatic import models


class Command(BaseCommand):
    help = "Load ajay's updates to instruments"

    def handle(self, *args, **options):
        fname = args[0]

        reader = csv.reader(open(fname, "rb"))
        next(reader)  # header
        for row in reader:
            name = row[0]
            percussion = row[2]
            row[4]
            picture = row[5]
            altpicture = row[6]
            row[7]
            source = row[8]
            description = row[9].decode("utf-8")

            print(name)

            i = models.Instrument.objects.get(name=name)
            i.percussion = not not percussion
            if not picture and altpicture:
                picture = altpicture
            if picture:
                print(f"downloading picture from {picture}")
                req = requests.get(picture, timeout=10)
                piccontents = req.content
                im = data.models.Image()
                im.image.save(f"{i.name}.jpg", ContentFile(piccontents))
                i.image = im
            if description:
                if source:
                    sn = data.models.SourceName.objects.get(name="Wikipedia")
                    sourceob, created = data.models.Source.objects.get_or_create(
                        source_name=sn, uri=source, defaults={"title": name}
                    )
                else:
                    sourceob = None
                descriptionob = data.models.Description.objects.create(description=description, source=sourceob)
                i.description = descriptionob
            i.save()
