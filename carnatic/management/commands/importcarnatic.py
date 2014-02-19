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

    def load(self, fname, obclass, has_tl, has_header):
        """ Load a csv file into a class. If any items are in
        additional columns then import them as aliases """
        fp = open(fname, "rb")
        reader = csv.reader(fp)
        if has_header:
            reader.next()
        for line in reader:
            name = line[0]
            print name
            tl = None
            if has_tl:
                tl = line[1]
                rest = line[3:]
            else:
                rest = line[1:]
            item, _ = obclass.objects.get_or_create(name=name)
            if has_tl and hasattr(item, "transliteration"):
                print "  transliteration", tl
                item.transliteration = tl
                item.save()
            if hasattr(obclass, "aliases"):
                for a in rest:
                    if a:
                        print "  alias", a
                        aob = item.aliases.filter(name=a)
                        if aob.count() == 0:
                            print "  - adding"
                            item.aliases.create(name=a)
                        else:
                            print "  - exists"

    def handle(self, *args, **options):
        if len(args) < 2:
            raise CommandError("Arguments: <instrument,raaga,taala,region,form,language,school> <csvfile>")
        t = args[0]
        fname = args[1]

        obclass = None
        # has transliteration. if this is the case then the columns
        # are name, transliteration, alt-name, aliases....
        has_tl = False
        # has header in the csv
        has_header = False
        if t == "instrument":
            obclass = Instrument
        elif t == "raaga":
            obclass = Raaga
            has_tl = True
            has_header = True
        elif t == "taala":
            obclass = Taala
            has_tl = True
            has_header = True
        elif t == "region":
            obclass = GeographicRegion
        elif t == "form":
            obclass = Form
        elif t == "language":
            obclass = Language
        elif t == "school":
            obclass = MusicalSchool
        if obclass:
            self.load(fname, obclass, has_tl, has_header)

