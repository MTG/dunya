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

from django.core.management.base import BaseCommand, CommandError

from hindustani import models


class Command(BaseCommand):
    help = "load hindustani data and aliases from a csv file"
    choices = ["raag", "taal", "laay", "form", "instrument"]

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
            raise CommandError("Arguments: <raag,taal,form,laay,instrument> <csvfile>")
        t = args[0]
        fname = args[1]

        obclass = None
        if t == "instrument":
            obclass = models.Instrument
        elif t == "form":
            obclass = models.Form
        elif t == "raag":
            obclass = models.Raag
        elif t == "taal":
            obclass = models.Taal
        elif t == "laay":
            obclass = models.Laya
        if obclass:
            self.load(fname, obclass)
