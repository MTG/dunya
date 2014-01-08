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
import csv

from carnatic.models import *

class Command(BaseCommand):
    help = "load data and aliases from a csv file"
    choices = ["instrument", "raaga", "taala", "region", "form", "language", "school"]

    def load(self, fname, obclass):
        """ Load a csv file into a class. If any items are in
        additional columns then import them as aliases """
        fp = open(fname, "rb")
        reader = csv.reader(fp)
        for line in reader:
            name = line[0]
            rest = line[1:]
            item, _ = obclass.objects.get_or_create(name=name)
            if hasattr(obclass, "aliases"):
                for a in rest:
                    if a:
                        item.aliases.create(name=a)

    def handle(self, *args, **options):
        if len(args) < 2:
            raise CommandError("Arguments: <instrument,raaga,taala,region,form,language,school> <csvfile>")
        t = args[0]
        fname = args[1]

        obclass = None
        if t == "instrument":
            obclass = Instrument
        elif t == "raaga":
            obclass = Raaga
        elif t == "taala":
            obclass = Taala
        elif t == "region":
            obclass = GeographicRegion
        elif t == "form":
            obclass = Form
        elif t == "language":
            obclass = Language
        elif t == "school":
            obclass = MusicalSchool
        if obclass:
            self.load(fname, obclass)

