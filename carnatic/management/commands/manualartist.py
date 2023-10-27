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


from compmusic import kutcheris
from compmusic import musicbrainz as mb
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

import data
from carnatic import models

mb.mb.set_hostname("musicbrainz.org")

# dunya id: Kutcheris id
themap = {38: 6,
          64: 103
          }


class Command(BaseCommand):
    help = 'Load biographies and images from kutcheris data'

    def handle(self, *args, **options):
        for did, kid in themap.items():
            a = models.Artist.objects.get(pk=did)
            print(f"* got {a.name} {a.mbid}")
            imgcontent, bio, wpurl = kutcheris.get_artist_details(kid)
            if bio:
                print("got bio")
                u = f"http://kutcheris.com/artist.php?id={kid}"
                sn = data.models.SourceName.objects.get(name="kutcheris.com")
                source, created = data.models.Source.objects.get_or_create(source_name=sn, uri=u,
                                                                           defaults={"title": a.name})
                description = data.models.Description.objects.create(description=bio, source=source)
                a.description = description

            if imgcontent:
                print("got image")
                im = data.models.Image()
                im.image.save(f"{a.mbid}.jpg", ContentFile(imgcontent))
                a.image = im
                a.save()

            # Check if they're on musicbrainz->wikipedia too
            print("looking up wikipedia")
            mba = mb.mb.get_artist_by_id(a.mbid, includes="url-rels")
            mba = mba["artist"]
            wikipedia = None
            for rel in mba.get("url-relation-list", []):
                if rel["type"] == "wikipedia":
                    wikipedia = rel["target"]
                    print(f"got wikipedia url {wikipedia}")
            theurl = None
            if wikipedia or wpurl:
                if wikipedia == wpurl:
                    theurl = wikipedia
                elif wikipedia and not wpurl:
                    theurl = wikipedia
                elif not wikipedia and wpurl:
                    theurl = wpurl
                else:
                    print("musicbrainz wp %s and kutcheris wp % are differnt. using mb" % (wikipedia, wpurl))
                    theurl = wikipedia
