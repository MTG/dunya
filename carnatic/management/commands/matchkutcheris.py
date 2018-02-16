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

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile

import csv
import os
import re
from carnatic import models
import data


class Command(BaseCommand):
    help = 'Load biographies and images from kutcheris data'

    def handle(self, *args, **options):
        fname = args[0]

        reader = csv.DictReader(open(fname, "rb"))
        for row in reader:
            name = row["artist"]
            bio = row["bio"]
            link = row["link"]
            print("Artist %s" % name)

            a = None
            try:
                a = models.Artist.objects.get(name=name)
            except models.Artist.DoesNotExist:
                m = re.search(r"[A-Z]\.[A-Z]", name)
                if m:
                    newname = re.sub(r"([A-Z]\.)([A-Z])", r"\1 \2", name)
                    try:
                        a = models.Artist.objects.get(name=newname)
                    except models.Artist.DoesNotExist:
                        pass
            if a:
                print("* got %s" % a.mbid)
                thedir = os.path.dirname(fname)
                photo = os.path.join(thedir, "photos", "%s.jpg" % name)
                if os.path.exists(photo):
                    if link:
                        sn = data.models.SourceName.objects.get(name="kutcheris.com")
                        source, created = data.models.Source.objects.get_or_create(source_name=sn, uri=link,
                                                                                   defaults={"title": a.name})
                    else:
                        source = None
                    description = data.models.Description.objects.create(description=bio, source=source)
                    a.description = description

                    im = data.models.Image()
                    im.image.save("%s.jpg" % a.mbid, ContentFile(open(photo, "rb").read()))
                    a.image = im
                    a.save()

            else:
                print("* not got")
