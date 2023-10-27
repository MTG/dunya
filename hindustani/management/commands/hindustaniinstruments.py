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
from hindustani import models


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
        next(reader)  # header
        for row in reader:
            _ = row[0]
            _ = row[1]
            name = row[2]
            percussion = row[3]
            hidden = row[4]
            alias = row[5]
            wikipedia = row[6]
            picture = row[7]
            description = row[8].decode("utf-8")

            print(name)

            i = models.Instrument.objects.fuzzy(name)
            i.percussion = not not percussion
            i.hidden = not not hidden

            if picture:
                print("downloading picture from", picture)
                req = requests.get(picture)
                piccontents = req.content
                im = data.models.Image()
                im.image.save(f"{i.name}.jpg", ContentFile(piccontents))
                i.image = im
                im.save()
            if description:
                if wikipedia:
                    sn = data.models.SourceName.objects.get(name="Wikipedia")
                    sourceob, created = data.models.Source.objects.get_or_create(source_name=sn, uri=wikipedia, defaults={"title": name})
                else:
                    sourceob = None
                descriptionob = data.models.Description.objects.create(description=description, source=sourceob)
                i.description = descriptionob
            i.save()
