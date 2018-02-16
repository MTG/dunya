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

from __future__ import print_function

import csv

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

import data
from carnatic import models


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
        reader.next()  # header
        for row in reader:
            name = row[0]
            percussion = row[2]
            wikipedia = row[4]
            picture = row[5]
            altpicture = row[6]
            altsource = row[7]
            source = row[8]
            description = row[9].decode("utf-8")

            print(name)

            i = models.Instrument.objects.get(name=name)
            i.percussion = not not percussion
            if not picture and altpicture:
                picture = altpicture
            if picture:
                print("downloading picture from %s" % picture)
                req = requests.get(picture)
                piccontents = req.content
                im = data.models.Image()
                im.image.save("%s.jpg" % i.name, ContentFile(piccontents))
                i.image = im
            if description:
                if source:
                    sn = data.models.SourceName.objects.get(name="Wikipedia")
                    sourceob, created = data.models.Source.objects.get_or_create(source_name=sn, uri=source,
                                                                                 defaults={"title": name})
                else:
                    sourceob = None
                descriptionob = data.models.Description.objects.create(description=description, source=sourceob)
                i.description = descriptionob
            i.save()
