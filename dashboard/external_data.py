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
from compmusic import file

def import_instrument_description(instrument, overwrite=False):
    iname = wikipedia.search(instrument.name)
    img, imgurl, b, u = wikipedia.get_artist_details(instrument.name)
    if b and b.startswith("#REDIR"):
        newname = b.replace("#REDIRECT ", "")
        img, imgurl, b, u = wikipedia.get_artist_details(newname)
    if b:
        sn = data.models.SourceName.objects.get(name="Wikipedia")
        source, created = data.models.Source.objects.get_or_create(source_name=sn, uri=u, defaults={"title": instrument.name})
        description = data.models.Description.objects.create(description=b, source=source)
        instrument.description = description
    if imgurl:
        sn = data.models.SourceName.objects.get(name="Wikipedia")
        source, created = data.models.Source.objects.get_or_create(source_name=sn, uri=imgurl, defaults={"title": instrument.name})
        imagefilename = instrument.name.replace(" ", "_")
        try:
            existingimg = instrument.images.get(image__contains="%s" % imagefilename)
            # TODO: If the image doesn't exist on disk this is an error. fix it.
            if existingimg.image.size != len(img) or overwrite:
                # If the imagesize has changed, or overwrite is set, remove the image
                existingimg.delete()
        except data.models.Image.DoesNotExist:
            pass

        im = data.models.Image()
        im.image.save("%s.jpg" % imagefilename, ContentFile(img))
        instrument.images.add(im)
    instrument.save()

def import_artist_bio(a, overwrite):
    artist = kutcheris.search_artist(a.name)
    additional_urls = []
    if not len(artist):
        print "Looing for data on wikipedia"
        i, iurl, b, u = wikipedia.get_artist_details(a.name)
        if u:
            additional_urls.append(u)
        #if not b:
        #    newname = wikipedia.search(a.name)
        #    mx = max(len(a.name), len(newname))
        #    mn = min(len(a.name), len(newname))
        #    # Only accept the wikipedia search result if it's
        #    if newname and mn + 3 < mx:
        #        i, b, u = wikipedia.get_artist_details(newname)
        if b:
            sn = data.models.SourceName.objects.get(name="Wikipedia")

    else:
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
        if i:
            print "Found image"

            try:
                existingimg = a.images.get(image__contains="%s" % a.mbid)
                # TODO: If the image doesn't exist on disk this is an error. fix it.
                #if existingimg.image.size != len(i) or overwrite:
                if overwrite:
                    # If the imagesize has changed, or overwrite is set, remove the image
                    existingimg.delete()
            except data.models.Image.DoesNotExist:
                pass

            im = data.models.Image()
            im.image.save("%s.jpg" % a.mbid, ContentFile(i))
            a.images.add(im)
        if additional_urls:
            for u in additional_urls:
                # Currently we only have wikipedia additionals, but this may change
                sn = data.models.SourceName.objects.get(name="Wikipedia")
                title = u.split("/")[-1].replace("_", " ")
                source, created = data.models.Source.objects.get_or_create(source_name=sn, uri=u, defaults={"title": title})
                a.references.add(source)
        a.save()

def import_concert_image(concert, directories=[], overwrite=False):
    for existing in concert.images.all():
        name = os.path.splitext(os.path.basename(existing.image.name))
        if name == concert.mbid:
            print "Image for concert %s exists, skipping" % concert.mbid
            return

    i = image.get_coverart_from_caa(concert.mbid)
    caa = True
    if not i:
        caa = False
        print "No image on CAA for %s, looking in directory" % concert.mbid
        i = image.get_coverart_from_directories(directories)
    if i:
        im = data.models.Image()
        if caa:
            uri = "http://archive.org/details/mbid-%s" % concert.mbid
            sn = data.models.SourceName.objects.get(name="Cover Art Archive")
            source, created = data.models.Source.objects.get_or_create(source_name=sn, uri=uri, defaults={"title": concert.title})
            im.source = source
        im.image.save("%s.jpg" % concert.mbid, ContentFile(i))

        # If the image is a different size from one that already exists, then
        # replace it
        try:
            existingimg = concert.images.get(image__contains="%s" % concert.mbid)
            if existingimg.image.size != len(i) or overwrite:
                # If the imagesize has changed, or overwrite is set, remove the image
                existingimg.delete()
        except data.models.Image.DoesNotExist:
            pass

        concert.images.add(im)
        concert.save()
    else:
        print "Can't find an image for %s" % concert.mbid

