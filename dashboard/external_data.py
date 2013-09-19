
from django.core.files.base import ContentFile

import data.models

from compmusic import wikipedia
from compmusic import kutcheris
from compmusic import image

def import_instrument_description(i):
    iname = wikipedia.search(i.name)
    img, b, u = wikipedia.get_artist_details(i.name)
    if b and b.startswith("#REDIR"):
        newname = b.replace("#REDIRECT ", "")
        img, b, u = wikipedia.get_artist_details(newname)
    if b:
        sn = data.models.SourceName.objects.get(name="Wikipedia")
        source = data.models.Source.objects.create(source_name=sn, title=i.name, uri=u)
        description = data.models.Description.objects.create(description=b, source=source)
        i.description = description
    if img:
        im = data.models.Image()
        im.image.save("/%s.jpg" % i.name.replace(" ", "_"), ContentFile(img))
        i.images.add(im)
    i.save()

def import_artist_bio(a):
    artist = kutcheris.search_artist(a.name)
    additional_urls = []
    if not len(artist):
        print "Looing for data on wikipedia"
        i, b, u = wikipedia.get_artist_details(a.name)
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
        i, b, u = kutcheris.get_artist_details(artist.values()[0])
        u = "http://kutcheris.com/artist.php?id=%s" % artist
        if b:
            sn = data.models.SourceName.objects.get(name="kutcheris.com")

    if b:
        source = data.models.Source.objects.create(source_name=sn, title=a.name, uri=u)
        description = data.models.Description.objects.create(description=b, source=source)
        a.description = description
        if i:
            print "Found image"
            im = data.models.Image()
            im.image.save("artist/%s.jpg" % a.mbid, ContentFile(i))
            a.images.add(im)
        if additional_urls:
            for u in additional_urls:
                # Currently we only have wikipedia additionals, but this may change
                sn = data.models.SourceName.objects.get(name="Wikipedia")
                source = data.models.Source.objects.create(source_name=sn, uri=u)
                a.references.add(source)
        a.save()

def import_concert_image(c):
    print "Loading coverart"
    i = image.get_coverart_for_release(c.mbid)
    if i:
        im = data.models.Image()
        im.image.save("concert/%s.jpg" % c.mbid, ContentFile(i))
        c.images.add(im)
        c.save()

