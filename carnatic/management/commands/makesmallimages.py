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

import os
from PIL import Image
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
import six

from carnatic import models


class Command(BaseCommand):
    help = 'Make mini versions of all images that are loaded'

    def make_small(self, item):
        print(item)
        img = item.image
        print(f"  {img}")

        size = 150, 150
        big = img.image
        fname = os.path.basename(big.name)
        smallfname = f"small_{fname}"
        try:
            pilimage = Image.open(big.path)
            out = six.BytesIO()
            pilimage.thumbnail(size)
            pilimage.save(out, "JPEG")

            img.small_image.save(smallfname, ContentFile(out.getvalue()))
            img.save()
        except IOError:
            pass

    def handle(self, *args, **options):
        instruments = models.Instrument.objects.all()
        for i in instruments:
            self.make_small(i)

        artists = models.Artist.objects.all()
        for a in artists:
            self.make_small(a)

        composers = models.Composer.objects.all()
        for c in composers:
            self.make_small(c)

        concerts = models.Concert.objects.all()
        for c in concerts:
            self.make_small(c)

        raagas = models.Raaga.objects.all()
        for r in raagas:
            self.make_small(r)

        taalas = models.Taala.objects.all()
        for t in taalas:
            self.make_small(t)
