from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile

import csv
import os
import re
from carnatic import models
from django.conf import settings
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
            print "Artist", name

            a = None
            try:
                a = models.Artist.objects.get(name=name)
            except models.Artist.DoesNotExist:
                m = re.search("[A-Z]\.[A-Z]", name)
                if m:
                    newname = re.sub("([A-Z]\.)([A-Z])", r"\1 \2", name)
                    try:
                        a = models.Artist.objects.get(name=newname)
                    except models.Artist.DoesNotExist:
                        pass
            if a:
                print "* got", a.mbid
                thedir = os.path.dirname(fname)
                photo = os.path.join(thedir, "photos", "%s.jpg" % name)
                if os.path.exists(photo):
                    if link:
                        sn = data.models.SourceName.objects.get(name="kutcheris.com")
                        source, created = data.models.Source.objects.get_or_create(source_name=sn, uri=link, defaults={"title": a.name})
                    else:
                        source = None
                    description = data.models.Description.objects.create(description=bio, source=source)
                    a.description = description
                    a.images.remove()

                    im = data.models.Image()
                    im.image.save("%s.jpg" % a.mbid, ContentFile(open(photo, "rb").read()))
                    a.images.add(im)
                    a.save()
                    
            else:
                print "* not got"
                
