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

from django.core.files.base import ContentFile
import os

import data.models

from compmusic import wikipedia
from compmusic import kutcheris
from compmusic import image

def import_artist_kutcheris(a):
    artist = kutcheris.search_artist(a.name)
    if artist:
        print "Found data on kutcheris.com"
        aid = artist.values()[0]
        i, b, u = kutcheris.get_artist_details(aid)
        u = "http://kutcheris.com/artist.php?id=%s" % aid
        if b:
            sn = data.models.SourceName.objects.get(name="kutcheris.com")

    if b:
        source, created = data.models.Source.objects.get_or_create(source_name=sn, uri=u, defaults={"title": a.name})
        description = data.models.Description.objects.create(description=b, source=source)
        a.description = description
        a.save()

def import_artist_wikipedia(artist):
    print "Looking for data on wikipedia"
    sn = data.models.SourceName.objects.get(name="Wikipedia")
    refs = artist.references.filter(source_name=sn)
    if refs.exists():
        source = refs.all()[0]
        wikiurl = source.uri
        name = os.path.basename(wikiurl)

        img, bio = wikipedia.get_artist_details(name)
        if bio:
            description = data.models.Description.objects.create(description=bio, source=source)
            # We call this with Composers too, which don't have `description_edited`
            # If d_edited is set, never overwrite it.
            if not getattr(artist, 'description_edited', False):
                artist.description = description
                artist.save()
        if img:
            try:
                existingimg = artist.images.get(image__contains="%s" % artist.mbid)
                if not os.path.exists(existingimg.image.path):
                    existingimg.delete()
                elif existingimg.image.size != len(img):
                    # If the imagesize has changed, remove the image
                    os.unlink(existingimg.image.path)
                    existingimg.delete()
            except data.models.Image.DoesNotExist:
                pass
            except data.models.Image.MultipleObjectsReturned:
                artist.images.filter(image__contains="%s" % artist.mbid).delete()

            im = data.models.Image()
            im.image.save("artist-%s.jpg" % artist.mbid, ContentFile(img))
            artist.images.add(im)

def import_release_image(release, directories=[]):
    for existing in release.images.all():
        name = os.path.splitext(os.path.basename(existing.image.name))
        if name == release.mbid:
            print "Image for release %s exists, skipping" % release.mbid
            return

    i = image.get_coverart_from_caa(release.mbid)
    caa = True
    if not i:
        caa = False
        print "No image on CAA for %s, looking in directory" % release.mbid
        i = image.get_coverart_from_directories(directories)
    if i:
        im = data.models.Image()
        if caa:
            uri = "http://archive.org/details/mbid-%s" % release.mbid
            sn = data.models.SourceName.objects.get(name="Cover Art Archive")
            source, created = data.models.Source.objects.get_or_create(source_name=sn, uri=uri, defaults={"title": release.title})
            im.source = source
        im.image.save("release-%s.jpg" % release.mbid, ContentFile(i))

        # If the image is a different size from one that already exists, then
        # replace it. Also remove if we have an item, but can't find the image
        # for it.
        try:
            existingimg = release.images.get(image__contains="%s" % release.mbid)
            haveimage = True
            if not os.path.exists(existingimg.image.path):
                existingimg.delete()
            elif existingimg.image.size != len(i):
                # If the imagesize has changed, remove it
                os.unlink(existingimg.image.path)
                existingimg.delete()
        except data.models.Image.DoesNotExist:
            haveimage = False

        # If we have an image, don't add it
        if not haveimage:
            release.images.add(im)
            release.save()
    else:
        print "Can't find an image for %s" % release.mbid
