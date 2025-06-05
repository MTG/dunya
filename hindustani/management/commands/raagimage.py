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

import collections
import os
from optparse import make_option

import numpy as np
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

import carnatic
import dashboard.extractors.similaritylib.raaga
import data
import hindustani
from docserver import util


class Command(BaseCommand):
    help = "Calculate mean pitch profile of all raags"

    option_list = BaseCommand.option_list + (
        make_option(
            "-d", action="store_true", dest="delete", default=False, help="Delete images for a raag(a) and reimport"
        ),
    )

    def calc_profile(self, raag, recordings, style):
        average = dashboard.extractors.similaritylib.raaga.Raaga(raag.name, "")
        pitches = []
        tonics = []
        for r in recordings:
            mbid = r.mbid
            try:
                pitch = util.docserver_get_json(mbid, "pitch", "pitch")
                tonic = util.docserver_get_contents(mbid, "votedtonic", "tonic")
                tonic = float(tonic)
                npp = np.array(pitch)
                pitches.append(npp)
                tonics.append(tonic)
            except util.NoFileException:
                pass

        average.compute_average_hist_data(pitches, tonics)

        if style == "carnatic":
            entityname = "raaga"
        elif style == "hindustani":
            entityname = "raag"
        fname = f"{style}-{entityname}-{raag.common_name.lower().replace(' ', '')}.png"
        average.generate_image(fname)
        im = data.models.Image()
        im.image.save(fname, ContentFile(open(fname, "rb").read()))
        raag.image = im
        raag.save()
        os.unlink(fname)

    def hindustani(self, delete):
        print("Creating hindustani raag images")
        recordings = hindustani.models.Recording.objects.all()
        recmap = collections.defaultdict(list)
        for r in recordings:
            if r.raags.count() == 1:
                raag = r.raags.get()
                recmap[raag].append(r)
        numraagas = len(recmap.keys())
        print("Got", numraagas, "raags")
        for i, (raag, recordings) in enumerate(recmap.items(), 1):
            print(f"({i}/{numraagas}) {raag}")
            create = True
            if raag.image:
                if delete:
                    try:
                        raag.image.image.delete()
                    except ValueError:
                        pass
                    raag.image.delete()
                    raag.image = None
                    raag.save()
                    print(" - Deleting images and remaking")
                else:
                    create = False
                    print(" - Image exists, skipping")
            if create:
                print(" - Making images")
                self.calc_profile(raag, recordings, "hindustani")

    def carnatic(self, delete):
        print("Creating carnatic raaga images")
        recordings = carnatic.models.Recording.objects.all()
        recmap = collections.defaultdict(list)
        for r in recordings:
            ra = r.raaga()
            if ra:
                recmap[ra].append(r)
        numraagas = len(recmap.keys())
        print("Got", numraagas, "raagas")
        for i, (raaga, recordings) in enumerate(recmap.items(), 1):
            print(f"({i}/{numraagas}) {raaga}")
            create = True
            if raaga.image:
                if delete:
                    try:
                        raaga.image.image.delete()
                    except ValueError:
                        pass
                    raaga.image.delete()
                    raaga.image = None
                    raaga.save()
                    print(" - Deleting images and remaking")
                else:
                    create = False
                    print(" - Image exists, skipping")
            if create:
                print(" - Making images")
                self.calc_profile(raaga, recordings, "carnatic")

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError("Arguments: [-d] <carnatic|hindustani>")
        if args[0] == "hindustani":
            self.hindustani(options["delete"])
        elif args[0] == "carnatic":
            self.carnatic(options["delete"])
