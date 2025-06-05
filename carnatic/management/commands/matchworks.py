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

from django.core.management.base import BaseCommand

from carnatic import models


class Command(BaseCommand):
    help = "Load vignesh's updates to works"

    def handle(self, *args, **options):
        fname = args[0]

        reader = csv.DictReader(open(fname, "rb"))
        for row in reader:
            id = row["ID"]
            workname = row["Work"]
            row["Composer"]
            raaga = row["Raaga"]
            taala = row["Taala"]
            row["Language"]
            form = row["Form"]
            print(f"work {workname}")

            w = models.Work.objects.get(pk=int(id))
            # TODO: Aliases
            f = models.Form.objects.fuzzy(form)
            w.form = f

            r = models.Raaga.objects.fuzzy(raaga)
            t = models.Taala.objects.fuzzy(taala)
            wrs = w.raaga.all()
            wts = w.taala.all()
            if wrs and r not in wrs:
                w.raaga.add(r)
            if wts and t not in wts:
                w.taala.add(t)
            w.save()
