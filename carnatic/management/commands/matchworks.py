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
    help = "Load vignesh's updates to works"

    def handle(self, *args, **options):
        fname = args[0]

        reader = csv.DictReader(open(fname, "rb"))
        for row in reader:
            id = row["ID"]
            workname = row["Work"]
            composer = row["Composer"]
            raaga = row["Raaga"]
            taala = row["Taala"]
            lang = row["Language"]
            form = row["Form"]
            print "work", workname

            w = models.Work.objects.get(pk=int(id))
            # TODO: Aliases
            l = models.Language.objects.fuzzy(lang)
            f = models.Form.objects.fuzzy(form)
            w.language = l
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
