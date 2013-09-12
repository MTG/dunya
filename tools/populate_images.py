import sys
import os
sys.path.insert(0, os.path.join(
        os.path.dirname(os.path.abspath(__file__)), ".."))

from dunya import settings
from django.core.management import setup_environ
setup_environ(settings)
from django.core.files.base import ContentFile

from carnatic.models import *
import data.models

from compmusic import wikipedia
from compmusic import kutcheris
from compmusic import image

def import_instrument(i):
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

def import_artist(a):
    artist = kutcheris.search_artist(a.name)
    additional_urls = []
    if not len(artist):
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
        i, b, u = kutcheris.get_artist_details(artist.values()[0])
        u = "http://kutcheris.com/artist.php?id=%s" % artist
        if b:
            sn = data.models.SourceName.objects.get(name="kutcheris.com")

    if b:
        source = data.models.Source.objects.create(source_name=sn, title=a.name, uri=u)
        description = data.models.Description.objects.create(description=b, source=source)
        a.description = description
        if i:
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

def import_concert(c):
    i = image.get_coverart_for_release(c.mbid)
    if i:
        im = data.models.Image()
        im.image.save("concert/%s.jpg" % c.mbid, ContentFile(i))
        c.images.add(im)
        c.save()

def do_artists():
    for a in Artist.objects.all():
        import_artist(a)

def do_composers():
    for c in Composer.objects.all():
        import_artist(c)

def do_concerts():
    for c in Concert.objects.all():
        import_concert(c)

if __name__ == "__main__":
    a = sys.argv[1]
    if a == "artist":
        do_artists()
    elif a == "composer":
        do_composers()
    elif a == "concert":
        do_concerts()
